"""Add order_index to ContextItem

Revision ID: 0003
Revises: 0002
Create Date: 2025-10-08 15:30:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0003"
down_revision = "0002_add_topic_slug"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add order_index column with default value 0
    op.add_column(
        "rag_contextitem",
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
    )

    # Remove server_default after migration (optional, keeps schema clean)
    op.alter_column("rag_contextitem", "order_index", server_default=None)


def downgrade() -> None:
    op.drop_column("rag_contextitem", "order_index")
