import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv(override=True)


@dataclass(frozen=True)
class ModelConfig:
    model: str = os.getenv("ALIBABA_MODEL", "qwen3.7-plus")
    model_provider: str = "openai"
    base_url: str | None = os.getenv("ALIBABA_API_URL")
    api_key: str | None = os.getenv("ALIBABA_API_KEY")


@dataclass(frozen=True)
class SearchConfig:
    max_results: int = int(os.getenv("TAVILY_MAX_RESULTS", "5"))
    topic: str = os.getenv("TAVILY_TOPIC", "general")


@dataclass(frozen=True)
class MemoryConfig:
    checkpoint_db_path: str = os.getenv("CHECKPOINT_DB_PATH", "./db/personal_chief.db")


@dataclass(frozen=True)
class AppConfig:
    model: ModelConfig = ModelConfig()
    search: SearchConfig = SearchConfig()
    memory: MemoryConfig = MemoryConfig()


settings = AppConfig()
