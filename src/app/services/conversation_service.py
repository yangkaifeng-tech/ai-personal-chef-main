from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Conversation, Message, User, utc_now
from app.auth.security import hash_password


def ensure_user(db: Session, user_id: str) -> User:
    user = db.get(User, user_id)
    if user:
        return user

    user = User(
        id=user_id,
        username=user_id,
        password_hash=hash_password(str(uuid4())),
        name=user_id,
        status="enabled",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_conversation(db: Session, user_id: str, title: str | None = None) -> Conversation:
    ensure_user(db, user_id)
    conversation = Conversation(
        user_id=user_id,
        thread_id=str(uuid4()),
        title=title or "新的私厨会话",
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_user_conversation(db: Session, user_id: str, conversation_id: str) -> Conversation:
    conversation = db.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != user_id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


def get_or_create_conversation(
    db: Session,
    user_id: str,
    conversation_id: str | None,
    title: str | None = None,
) -> Conversation:
    if conversation_id:
        return get_user_conversation(db, user_id, conversation_id)
    return create_conversation(db, user_id, title)


def list_user_conversations(db: Session, user_id: str) -> list[Conversation]:
    ensure_user(db, user_id)
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    return list(db.scalars(statement))


def list_conversation_messages(db: Session, user_id: str, conversation_id: str) -> list[Message]:
    conversation = get_user_conversation(db, user_id, conversation_id)
    return list(conversation.messages)


def append_message(
    db: Session,
    conversation_id: str,
    role: str,
    content: str,
    image_url: str | None = None,
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        image_url=image_url,
    )
    conversation = db.get(Conversation, conversation_id)
    if conversation:
        conversation.updated_at = utc_now()
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def clear_conversation(db: Session, user_id: str, conversation_id: str) -> Conversation:
    conversation = get_user_conversation(db, user_id, conversation_id)
    for message in list(conversation.messages):
        db.delete(message)
    conversation.updated_at = utc_now()
    db.commit()
    db.refresh(conversation)
    return conversation
