"""add contextitem order_index index"""

from alembic import op

revision = "0004"
down_revision = "e26f3ba7cd58"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_rag_contextitem_order_index",
        "rag_contextitem",
        ["order_index"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_rag_contextitem_order_index", table_name="rag_contextitem")
