"""add feedback comment to question history"""

import sqlalchemy as sa

from alembic import op

revision = "e26f3ba7cd58"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "rag_questionhistory",
        sa.Column("feedback_comment", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("rag_questionhistory", "feedback_comment")
