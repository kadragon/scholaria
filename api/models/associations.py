"""Association tables shared across SQLAlchemy models."""

from sqlalchemy import BigInteger, Column, ForeignKey, Table

from api.models.base import Base

# Mirror Django-generated ManyToMany join table between Topic and Context.
topic_context_association = Table(
    "rag_topic_contexts",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("topic_id", ForeignKey("rag_topic.id", ondelete="CASCADE"), nullable=False),
    Column(
        "context_id", ForeignKey("rag_context.id", ondelete="CASCADE"), nullable=False
    ),
)
