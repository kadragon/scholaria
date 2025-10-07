"""add_topic_slug

Revision ID: 0002_add_topic_slug
Revises: 990a42024f17
Create Date: 2025-10-07 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_add_topic_slug"
down_revision: str | None = "990a42024f17"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("rag_topic", sa.Column("slug", sa.String(length=50), nullable=True))

    bind = op.get_bind()
    from sqlalchemy.orm import Session

    from backend.services.slug_utils import ensure_unique_slug, generate_slug

    session = Session(bind=bind)
    topics = session.execute(sa.text("SELECT id, name FROM rag_topic")).fetchall()

    for topic_id, name in topics:
        base_slug = generate_slug(name)
        unique_slug = ensure_unique_slug(base_slug, session)
        session.execute(
            sa.text("UPDATE rag_topic SET slug = :slug WHERE id = :id"),
            {"slug": unique_slug, "id": topic_id},
        )
    session.commit()

    op.alter_column("rag_topic", "slug", nullable=False)
    op.create_unique_constraint("uq_rag_topic_slug", "rag_topic", ["slug"])
    op.create_index("ix_rag_topic_slug", "rag_topic", ["slug"])


def downgrade() -> None:
    op.drop_index("ix_rag_topic_slug", table_name="rag_topic")
    op.drop_constraint("uq_rag_topic_slug", "rag_topic", type_="unique")
    op.drop_column("rag_topic", "slug")
