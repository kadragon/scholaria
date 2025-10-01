"""SQLAlchemy base configuration."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.config import settings

SessionLocal = sessionmaker(autocommit=False, autoflush=False)

_engine: Engine | None = None
_engine_signature: tuple[str, tuple[tuple[str, Any], ...]] | None = None


def _ensure_engine() -> Engine:
    """Create or reuse SQLAlchemy engine based on current settings."""

    global _engine, _engine_signature

    database_url, connect_args = settings.database_config()
    signature = (database_url, tuple(sorted(connect_args.items())))

    if _engine is None or signature != _engine_signature:
        _engine = create_engine(
            database_url,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            connect_args=connect_args,
        )
        SessionLocal.configure(bind=_engine)
        _engine_signature = signature

    return _engine


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


def get_db() -> Generator[Session]:
    """Dependency for database sessions."""
    _ensure_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
