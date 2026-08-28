import sqlite3

from langchain.messages import AIMessage, HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver

from app.core.config import settings


def build_agent_thread_id(thread_id: str) -> str:
    return f"{thread_id}:agent-text"


def create_checkpointer() -> SqliteSaver:
    backend = settings.memory.checkpoint_backend.lower()
    if backend == "postgres":
        return create_postgres_checkpointer()
    if backend == "sqlite":
        return create_sqlite_checkpointer()
    raise ValueError(f"Unsupported CHECKPOINT_BACKEND: {settings.memory.checkpoint_backend}")


def create_sqlite_checkpointer() -> SqliteSaver:
    connection = sqlite3.connect(settings.memory.sqlite_checkpoint_db_path, check_same_thread=False)
    checkpointer = SqliteSaver(connection)
    checkpointer.setup()
    return checkpointer


def create_postgres_checkpointer():
    if not settings.memory.postgres_checkpoint_database_url:
        raise RuntimeError("POSTGRES_CHECKPOINT_DATABASE_URL is required when CHECKPOINT_BACKEND=postgres.")

    try:
        import psycopg
        from langgraph.checkpoint.postgres import PostgresSaver
        from psycopg.rows import dict_row
    except ImportError as error:
        raise RuntimeError(
            "PostgreSQL checkpoint requires psycopg and langgraph-checkpoint-postgres."
        ) from error

    database_url = settings.memory.postgres_checkpoint_database_url.replace(
        "postgresql+psycopg://",
        "postgresql://",
        1,
    )
    connection = psycopg.connect(
        database_url,
        autocommit=True,
        row_factory=dict_row,
    )
    checkpointer = PostgresSaver(connection)
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
