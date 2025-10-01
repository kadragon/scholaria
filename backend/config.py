"""FastAPI application configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings sourced from environment variables."""

    DEBUG: bool = Field(default=True)

    JWT_SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_HOURS: int = Field(default=24)

    DB_ENGINE: str = Field(default="postgresql")
    DB_NAME: str = Field(default="scholaria")
    DB_USER: str = Field(default="postgres")
    DB_PASSWORD: str = Field(default="")
    DB_HOST: str = Field(default="localhost")
    DB_PORT: str = Field(default="5432")

    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: str = Field(default="6379")
    REDIS_DB: str = Field(default="0")

    FASTAPI_ALLOWED_ORIGINS: str = Field(
        default="http://localhost:8000,http://localhost:3000,http://localhost:5173"
    )

    OPENAI_API_KEY: str | None = Field(default=None)
    OPENAI_EMBEDDING_MODEL: str = Field(default="text-embedding-3-large")
    OPENAI_EMBEDDING_DIM: int = Field(default=3072)
    OPENAI_CHAT_MODEL: str = Field(default="gpt-4o-mini")
    OPENAI_CHAT_TEMPERATURE: float = Field(default=0.3)
    OPENAI_CHAT_MAX_TOKENS: int = Field(default=1000)

    RAG_SEARCH_LIMIT: int = Field(default=10)
    RAG_RERANK_TOP_K: int = Field(default=5)

    LLAMAINDEX_CACHE_ENABLED: bool = Field(default=False)
    LLAMAINDEX_CACHE_DIR: str = Field(default="storage/llamaindex_cache")
    LLAMAINDEX_CACHE_NAMESPACE: str = Field(default="scholaria-default")

    database_url_override: str | None = Field(default=None, alias="DATABASE_URL")

    @property
    def redis_url(self) -> str:
        """Redis connection URL."""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def cors_origins(self) -> list[str]:
        """Parse CORS allowed origins from comma-separated string."""
        if not self.FASTAPI_ALLOWED_ORIGINS:
            return []
        return [origin.strip() for origin in self.FASTAPI_ALLOWED_ORIGINS.split(",")]

    def database_config(self) -> tuple[str, dict[str, Any]]:
        """Return (SQLAlchemy URL, connect_args) derived from environment."""

        if self.database_url_override:
            return self.database_url_override, {}

        db_config = self._active_db_config()

        engine_key = db_config["ENGINE"].lower()
        if "sqlite" in engine_key:
            db_name = str(db_config["NAME"])
            if db_name == ":memory:":
                # In-memory sqlite should still be shared across threads
                return "sqlite+pysqlite:///:memory:", {"check_same_thread": False}

            db_path = Path(db_name)
            if not db_path.is_absolute():
                project_root = Path(__file__).resolve().parents[2]
                db_path = (project_root / db_path).resolve()

            return f"sqlite+pysqlite:///{db_path}", {"check_same_thread": False}

        user = quote_plus(str(db_config.get("USER", self.DB_USER)))
        raw_password = db_config.get("PASSWORD", self.DB_PASSWORD)
        password_value = "" if raw_password is None else str(raw_password)
        password = quote_plus(password_value) if password_value else ""
        host = str(db_config.get("HOST", self.DB_HOST))
        port = str(db_config.get("PORT", self.DB_PORT))
        db_name = str(db_config.get("NAME", self.DB_NAME))
        credentials = f"{user}:{password}@" if password else f"{user}@"
        return (
            f"postgresql+psycopg://{credentials}{host}:{port}/{db_name}",
            {},
        )

    @property
    def DATABASE_URL(self) -> str:  # noqa: N802 (maintain legacy attribute name)
        """Expose SQLAlchemy URL for backwards compatibility."""
        url, _ = self.database_config()
        return url

    def _active_db_config(self) -> dict[str, Any]:
        """Resolve database config from Django settings when available."""

        return {
            "ENGINE": self.DB_ENGINE,
            "NAME": self.DB_NAME,
            "USER": self.DB_USER,
            "PASSWORD": self.DB_PASSWORD,
            "HOST": self.DB_HOST,
            "PORT": self.DB_PORT,
        }


settings = Settings()
