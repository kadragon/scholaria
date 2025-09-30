"""
SQLAlchemy Topic model.

Equivalent to Django rag.models.Topic.
POC version - simplified without relationships.
"""

from datetime import datetime

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from api.models.base import Base


class Topic(Base):
    __tablename__ = "rag_topic"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Topic(id={self.id}, name='{self.name}')>"
