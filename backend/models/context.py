"""
SQLAlchemy Context model.

Equivalent to Django rag.models.Context.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from backend.models.associations import topic_context_association
from backend.models.base import Base

if TYPE_CHECKING:
    from backend.models.topic import Topic


class Context(Base):
    __tablename__ = "rag_context"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    context_type: Mapped[str] = mapped_column(String(20), nullable=False)
    original_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    processing_status: Mapped[str] = mapped_column(
        String(20), default="PENDING", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationship to ContextItem
    items: Mapped[list["ContextItem"]] = relationship(
        "ContextItem",
        back_populates="context",
        lazy="select",
        cascade="all, delete-orphan",
    )
    topics: Mapped[list["Topic"]] = relationship(
        "Topic",
        secondary=topic_context_association,
        back_populates="contexts",
        lazy="selectin",
        order_by="Topic.id",
    )

    def __repr__(self) -> str:
        return (
            f"<Context(id={self.id}, name='{self.name}', type='{self.context_type}')>"
        )


class ContextItem(Base):
    __tablename__ = "rag_contextitem"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    context_id: Mapped[int] = mapped_column(
        ForeignKey("rag_context.id"), nullable=False, index=True
    )
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Note: Django field name is 'metadata' but it's reserved in SQLAlchemy
    # We map to the same DB column name
    item_metadata: Mapped[str | None] = mapped_column(
        "metadata", Text, nullable=True
    )  # JSON stored as text
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationship to Context
    context: Mapped["Context"] = relationship("Context", back_populates="items")

    def __repr__(self) -> str:
        return f"<ContextItem(id={self.id}, title='{self.title}')>"
