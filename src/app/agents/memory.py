import sqlite3

from langchain.messages import AIMessage, HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver

from app.core.config import settings


def build_agent_thread_id(thread_id: str) -> str:
    return f"{thread_id}:agent-text"


def create_checkpointer() -> SqliteSaver:
    connection = sqlite3.connect(settings.memory.checkpoint_db_path, check_same_thread=False)
    checkpointer = SqliteSaver(connection)
    checkpointer.setup()
    return checkpointer


def clear_thread_messages(checkpointer: SqliteSaver, thread_id: str) -> None:
    checkpointer.delete_thread(thread_id)
    checkpointer.delete_thread(build_agent_thread_id(thread_id))


def get_messages_from_checkpointer(checkpointer: SqliteSaver, thread_id: str) -> list[dict[str, str]]:
    checkpoint = checkpointer.get({
        "configurable": {"thread_id": build_agent_thread_id(thread_id)}
    })

    if not checkpoint:
        return []

    channel_values = checkpoint.get("channel_values")
    if not channel_values:
        return []

    messages = channel_values.get("messages", [])
    if not messages:
        return []

    result = []
    for msg in messages:
        if not msg.content:
            continue

        if isinstance(msg, HumanMessage):
            result.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            result.append({"role": "assistant", "content": msg.content})

    return result
