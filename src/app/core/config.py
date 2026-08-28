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
    checkpoint_backend: str = os.getenv("CHECKPOINT_BACKEND", "postgres")
    sqlite_checkpoint_db_path: str = os.getenv(
        "SQLITE_CHECKPOINT_DB_PATH",
        os.getenv("CHECKPOINT_DB_PATH", "./db/personal_chief.db"),
    )
    postgres_checkpoint_database_url: str | None = os.getenv(
        "POSTGRES_CHECKPOINT_DATABASE_URL",
        os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/personal_chef"),
    )


@dataclass(frozen=True)
class DatabaseConfig:
    url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/personal_chef",
    )


@dataclass(frozen=True)
class AuthConfig:
    jwt_secret: str = os.getenv("JWT_SECRET", "change-this-secret-in-production")
    jwt_expires_minutes: int = int(os.getenv("JWT_EXPIRES_MINUTES", "1440"))
    default_admin_username: str = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    default_admin_password: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")


@dataclass(frozen=True)
class AppConfig:
    model: ModelConfig = ModelConfig()
    search: SearchConfig = SearchConfig()
    memory: MemoryConfig = MemoryConfig()
    database: DatabaseConfig = DatabaseConfig()
    auth: AuthConfig = AuthConfig()


settings = AppConfig()
