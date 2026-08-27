from langchain.messages import AIMessageChunk, HumanMessage, ToolMessage

from app.agents.factory import get_personal_chef_runtime
from app.agents.memory import (
    build_agent_thread_id,
    clear_thread_messages,
    get_messages_from_checkpointer,
)
from app.agents.prompts import build_recipe_message
from app.agents.vision import identify_ingredients
from app.common.logger import logger


def chunk_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        return "".join(text_parts)
    return ""


#流式对话
async def search_recipes(prompt: str, image: str, thread_id: str):
    """调用agent搜索食谱"""
    runtime = get_personal_chef_runtime()
    logger.info(f"[用户】：{prompt}, image: {image}, thread_id: {thread_id}")
    agent_thread_id = build_agent_thread_id(thread_id)

    try:
        # 判断是否有图片
        if not image or image.strip() == "":
            message = HumanMessage(content=prompt)
        else:
            ingredients = await identify_ingredients(runtime.model, image)
            logger.info(f"[图片识别结果]: {ingredients}")
            message = HumanMessage(content=build_recipe_message(prompt, ingredients))

        # 流式调用 agents
        for chunk, metadata in runtime.agent.stream(
                {"messages": [message]},
                {"configurable": {"thread_id": agent_thread_id}},
                stream_mode="messages"
        ):
            if isinstance(chunk, AIMessageChunk) and chunk.tool_call_chunks:
                logger.info(f"[工具调用中]: {chunk.tool_call_chunks}")
                continue
            elif isinstance(chunk, ToolMessage):
                logger.info(f"[工具调用结果]: {chunk.name}: {chunk.content}")
                continue

            if isinstance(chunk, AIMessageChunk):
                text = chunk_text(chunk.content)
                if text:
                    yield text

    except Exception as e:
        logger.error(f"\n[错误]: {str(e)}")
        yield "信息检索失败，试试看手动输入食物列表？"

#清空对话
def clear_messages(thread_id: str):
    """清空对话"""
    logger.info(f"清空历史消息：thread_id: {thread_id}")
    runtime = get_personal_chef_runtime()
    clear_thread_messages(runtime.checkpointer, thread_id)

#查询历史消息
def get_messages(thread_id: str) -> list[dict[str, str]]:
    """查询历史消息"""
    logger.info(f"获取历史消息：thread_id: {thread_id}")
    runtime = get_personal_chef_runtime()
    return get_messages_from_checkpointer(runtime.checkpointer, thread_id)
