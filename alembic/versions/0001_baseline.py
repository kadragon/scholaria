"""Baseline revision for existing Django-managed schema."""

# revision identifiers, used by Alembic.
revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Mark current schema as baseline without applying changes."""
    # No-op: Django migrations already created the schema.
    pass


def downgrade() -> None:
    """Reverting baseline is a no-op."""
    pass
