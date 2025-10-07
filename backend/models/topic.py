"""SQLAlchemy Topic model mirroring Django ``rag.models.Topic``."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, event, text
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from backend.models.associations import topic_context_association
from backend.models.base import Base

if TYPE_CHECKING:
    from backend.models.context import Context
    from backend.models.history import QuestionHistory


class Topic(Base):
    __tablename__ = "rag_topic"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("(CURRENT_TIMESTAMP)"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("(CURRENT_TIMESTAMP)"),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    contexts: Mapped[list[Context]] = relationship(
        "Context",
        secondary=topic_context_association,
        back_populates="topics",
        lazy="selectin",
        order_by="Context.id",
    )
    question_histories: Mapped[list[QuestionHistory]] = relationship(
        "QuestionHistory",
        back_populates="topic",
        lazy="select",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Topic(id={self.id}, name='{self.name}')>"


@event.listens_for(Topic, "before_insert")
def generate_slug_before_insert(
    mapper: object, connection: object, target: Topic
) -> None:
    from sqlalchemy.engine import Connection

    from backend.services.slug_utils import ensure_unique_slug, generate_slug

    if not target.slug or target.slug == "":
        session = Session.object_session(target) or Session(
            bind=connection if isinstance(connection, Connection) else None
        )
        base_slug = generate_slug(target.name)
        target.slug = ensure_unique_slug(base_slug, session)
