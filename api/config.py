"""
FastAPI application configuration.
"""

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    DB_ENGINE: str = os.getenv("DB_ENGINE", "postgresql")
    DB_NAME: str = os.getenv("DB_NAME", "scholaria")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")

    @property
    def DATABASE_URL(self) -> str:
        """Construct PostgreSQL database URL with psycopg (binary) driver."""
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
