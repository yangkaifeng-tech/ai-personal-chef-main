import asyncio
import json

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.agents.personal_chief import search_recipes, get_messages, clear_messages
from app.auth.dependencies import get_current_user
from app.db.models import User
from app.db.session import SessionLocal, get_db
from app.models.schemas import ChatRequest
from app.services.conversation_service import (
    append_message,
    clear_conversation,
    get_or_create_conversation,
    list_conversation_messages,
    list_user_conversations,
)

router = APIRouter()


def serialize_conversation(conversation):
    return {
        "id": conversation.id,
        "title": conversation.title,
        "thread_id": conversation.thread_id,
        "agent_type": conversation.agent_type,
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
    }


def serialize_message(message):
    return {
        "id": message.id,
        "role": message.role,
        "content": message.content,
        "image_url": message.image_url,
        "created_at": message.created_at.isoformat(),
    }


def sse_event(event: str, payload: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.post("/chat/stream")
def chat_endpoint(
    request: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """流式对话"""
    title = request.message[:30] if request.message else "新的私厨会话"
    conversation = get_or_create_conversation(db, user.id, request.conversation_id, title)
    conversation_id = conversation.id
    conversation_thread_id = conversation.thread_id
    user_content = request.message or "这是我现有的食材，请推荐适合的菜谱。"
    append_message(db, conversation_id, "user", user_content, request.image_url)
    # StreamingResponse 会让依赖注入的 db session 延迟关闭。
    # append_message 内部 refresh 后会开启一个新事务，如果这里不主动结束，
    # PostgreSQL checkpoint 的 CREATE INDEX CONCURRENTLY 可能会等待这个旧事务。
    db.rollback()

    def save_assistant_message(answer: str) -> None:
        with SessionLocal() as save_db:
            append_message(save_db, conversation_id, "assistant", answer)

    async def stream_and_save():
        answer = ""
        yield sse_event("conversation", {"conversation_id": conversation_id})
        yield sse_event(
            "status",
            {"content": "正在识别图片食材..." if request.image_url else "正在检索菜谱..."},
        )
        async for chunk in search_recipes(user_content, request.image_url, conversation_thread_id):
            answer += chunk
            yield sse_event("message", {"content": chunk})
        if answer.strip():
            await asyncio.to_thread(save_assistant_message, answer)
        yield sse_event("done", {})

    return StreamingResponse(stream_and_save(), media_type="text/event-stream")


@router.get("/chat/messages")
def get_chat_messages(
    thread_id: str | None = None,
    conversation_id: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取历史消息"""
    if conversation_id:
        messages = [
            serialize_message(message)
            for message in list_conversation_messages(db, user.id, conversation_id)
        ]
        return {"messages": messages}

    if not thread_id:
        return {"messages": []}

    messages = get_messages(thread_id)
    return {"messages": messages}


@router.delete("/chat/messages")
def clear_chat_messages(
    thread_id: str | None = None,
    conversation_id: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """清空历史消息"""
    if conversation_id:
        conversation = clear_conversation(db, user.id, conversation_id)
        clear_messages(conversation.thread_id)
        return {"success": True}

    if thread_id:
        clear_messages(thread_id)
    return {"success": True}


@router.get("/conversations")
def get_conversations(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """获取用户会话列表"""
    conversations = list_user_conversations(db, user.id)
    return {"conversations": [serialize_conversation(conversation) for conversation in conversations]}


@router.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(
    conversation_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取指定会话消息"""
    messages = list_conversation_messages(db, user.id, conversation_id)
    return {"messages": [serialize_message(message) for message in messages]}


@router.delete("/conversations/{conversation_id}")
def delete_conversation_messages(
    conversation_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """清空指定会话消息"""
    conversation = clear_conversation(db, user.id, conversation_id)
    clear_messages(conversation.thread_id)
    return {"success": True}
