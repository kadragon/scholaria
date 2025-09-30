"""FastAPI application configuration."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings sourced from environment variables."""

    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", "your-secret-key-change-in-production"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_HOURS: int = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRE_HOURS", "24")
    )

    DB_ENGINE: str = os.getenv("DB_ENGINE", "postgresql")
    DB_NAME: str = os.getenv("DB_NAME", "scholaria")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")

    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: str = os.getenv("REDIS_PORT", "6379")
    REDIS_DB: str = os.getenv("REDIS_DB", "0")

    database_url_override: str | None = Field(default=None, alias="DATABASE_URL")

    @property
    def redis_url(self) -> str:
        """Redis connection URL."""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

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
        password = quote_plus(str(db_config.get("PASSWORD", self.DB_PASSWORD)))
        host = str(db_config.get("HOST", self.DB_HOST))
        port = str(db_config.get("PORT", self.DB_PORT))
        db_name = str(db_config.get("NAME", self.DB_NAME))
        return (
            f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db_name}",
            {},
        )

    @property
    def DATABASE_URL(self) -> str:  # noqa: N802 (maintain legacy attribute name)
        """Expose SQLAlchemy URL for backwards compatibility."""
        url, _ = self.database_config()
        return url

    def _active_db_config(self) -> dict[str, Any]:
        """Resolve database config from Django settings when available."""

        db_config: dict[str, Any] = {
            "ENGINE": self.DB_ENGINE,
            "NAME": self.DB_NAME,
            "USER": self.DB_USER,
            "PASSWORD": self.DB_PASSWORD,
            "HOST": self.DB_HOST,
            "PORT": self.DB_PORT,
        }

        try:
            from django.conf import settings as django_settings

            if django_settings.configured and "default" in django_settings.DATABASES:
                django_db = django_settings.DATABASES["default"]
                db_config.update(  # prioritize Django test/runtime settings
                    {
                        "ENGINE": django_db.get("ENGINE", db_config["ENGINE"]),
                        "NAME": django_db.get("NAME", db_config["NAME"]),
                        "USER": django_db.get("USER", db_config["USER"]),
                        "PASSWORD": django_db.get("PASSWORD", db_config["PASSWORD"]),
                        "HOST": django_db.get("HOST", db_config["HOST"]),
                        "PORT": django_db.get("PORT", db_config["PORT"]),
                    }
                )
        except Exception:
            # Django not installed/configured; fall back to environment values
            pass

        return db_config


settings = Settings()
