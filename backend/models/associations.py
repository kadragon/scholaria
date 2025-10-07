"""Association tables shared across SQLAlchemy models."""

from sqlalchemy import Column, ForeignKey, Table

from backend.models.base import Base

# Mirror Django-generated ManyToMany join table between Topic and Context.
topic_context_association = Table(
    "rag_topic_contexts",
    Base.metadata,
    Column(
        "topic_id",
        ForeignKey("rag_topic.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "context_id",
        ForeignKey("rag_context.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
)
