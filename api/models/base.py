"""
SQLAlchemy base configuration.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from api.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


def get_db() -> Generator[Session, None, None]:
    """Dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
