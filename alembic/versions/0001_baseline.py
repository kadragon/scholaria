"""Baseline revision for existing Django-managed schema."""

# revision identifiers, used by Alembic.
revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables for fresh database."""
    import sqlalchemy as sa

    from alembic import op

    op.create_table(
        "auth_user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("password", sa.String(length=128), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_staff", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "first_name", sa.String(length=150), nullable=False, server_default=""
        ),
        sa.Column(
            "last_name", sa.String(length=150), nullable=False, server_default=""
        ),
        sa.Column(
            "date_joined",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_auth_user_id"), "auth_user", ["id"], unique=False)
    op.create_index(
        op.f("ix_auth_user_username"), "auth_user", ["username"], unique=True
    )
    op.create_index(op.f("ix_auth_user_email"), "auth_user", ["email"], unique=True)

    op.create_table(
        "rag_topic",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("system_prompt", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            onupdate=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rag_topic_id"), "rag_topic", ["id"], unique=False)
    op.create_index(op.f("ix_rag_topic_name"), "rag_topic", ["name"], unique=False)

    op.create_table(
        "rag_context",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("context_type", sa.String(length=20), nullable=False),
        sa.Column("original_content", sa.Text(), nullable=True),
        sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "processing_status",
            sa.String(length=20),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            onupdate=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rag_context_id"), "rag_context", ["id"], unique=False)
    op.create_index(op.f("ix_rag_context_name"), "rag_context", ["name"], unique=False)

    op.create_table(
        "rag_contextitem",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("context_id", sa.Integer(), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            onupdate=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["context_id"], ["rag_context.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_rag_contextitem_id"), "rag_contextitem", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_rag_contextitem_context_id"),
        "rag_contextitem",
        ["context_id"],
        unique=False,
    )

    op.create_table(
        "rag_questionhistory",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("session_id", sa.String(length=255), nullable=False),
        sa.Column("is_favorited", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            onupdate=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["topic_id"], ["rag_topic.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_rag_questionhistory_id"), "rag_questionhistory", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_rag_questionhistory_topic_id"),
        "rag_questionhistory",
        ["topic_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_rag_questionhistory_session_id"),
        "rag_questionhistory",
        ["session_id"],
        unique=False,
    )

    op.create_table(
        "rag_topic_contexts",
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("context_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["context_id"], ["rag_context.id"]),
        sa.ForeignKeyConstraint(["topic_id"], ["rag_topic.id"]),
        sa.PrimaryKeyConstraint("topic_id", "context_id"),
    )


def downgrade() -> None:
    """Drop all tables."""
    from alembic import op

    op.drop_table("rag_topic_contexts")
    op.drop_index(
        op.f("ix_rag_questionhistory_session_id"), table_name="rag_questionhistory"
    )
    op.drop_index(
        op.f("ix_rag_questionhistory_topic_id"), table_name="rag_questionhistory"
    )
    op.drop_index(op.f("ix_rag_questionhistory_id"), table_name="rag_questionhistory")
    op.drop_table("rag_questionhistory")
    op.drop_index(op.f("ix_rag_contextitem_context_id"), table_name="rag_contextitem")
    op.drop_index(op.f("ix_rag_contextitem_id"), table_name="rag_contextitem")
    op.drop_table("rag_contextitem")
    op.drop_index(op.f("ix_rag_context_name"), table_name="rag_context")
    op.drop_index(op.f("ix_rag_context_id"), table_name="rag_context")
    op.drop_table("rag_context")
    op.drop_index(op.f("ix_rag_topic_name"), table_name="rag_topic")
    op.drop_index(op.f("ix_rag_topic_id"), table_name="rag_topic")
    op.drop_table("rag_topic")
    op.drop_index(op.f("ix_auth_user_email"), table_name="auth_user")
    op.drop_index(op.f("ix_auth_user_username"), table_name="auth_user")
    op.drop_index(op.f("ix_auth_user_id"), table_name="auth_user")
    op.drop_table("auth_user")
