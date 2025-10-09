"""SQLAlchemy model for QuestionHistory."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base

if TYPE_CHECKING:
    from backend.models.topic import Topic


class QuestionHistory(Base):
    """SQLAlchemy representation of rag_questionhistory."""

    __tablename__ = "rag_questionhistory"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("rag_topic.id"), nullable=False, index=True
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    is_favorited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    feedback_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    feedback_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("(CURRENT_TIMESTAMP)"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("(CURRENT_TIMESTAMP)"),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    topic: Mapped[Topic] = relationship("Topic", back_populates="question_histories")

    def __repr__(self) -> str:
        return f"<QuestionHistory(id={self.id}, topic_id={self.topic_id})>"
