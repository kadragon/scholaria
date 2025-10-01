"""add_feedback_score"""

import sqlalchemy as sa

from alembic import op

revision = "990a42024f17"
down_revision = "0001_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "rag_questionhistory",
        sa.Column("feedback_score", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("rag_questionhistory", "feedback_score")
