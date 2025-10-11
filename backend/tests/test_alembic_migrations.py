"""Tests for Alembic migration 0004 - add order_index to contextitem."""

import pytest
from sqlalchemy import inspect, text

from backend.models.base import _ensure_engine


@pytest.mark.skipif(
    True,
    reason="Migration tests require Postgres. Run in Docker: docker compose exec backend bash -lc 'cd backend && uv run pytest tests/test_alembic_migrations.py'",
)
def test_0004_order_index_exists_after_migration() -> None:
    """Migration 0004 should create ix_rag_contextitem_order_index."""
    engine = _ensure_engine()
    inspector = inspect(engine)
    indexes = {idx["name"] for idx in inspector.get_indexes("rag_contextitem")}
    assert "ix_rag_contextitem_order_index" in indexes


@pytest.mark.skipif(
    True,
    reason="Migration tests require Postgres. Run in Docker: docker compose exec backend bash -lc 'cd backend && uv run pytest tests/test_alembic_migrations.py'",
)
def test_0004_order_index_covers_order_index_column() -> None:
    """Index should cover order_index column."""
    engine = _ensure_engine()
    inspector = inspect(engine)
    indexes = inspector.get_indexes("rag_contextitem")
    order_index_idx = next(
        (idx for idx in indexes if idx["name"] == "ix_rag_contextitem_order_index"),
        None,
    )
    assert order_index_idx is not None
    assert order_index_idx["column_names"] == ["order_index"]


@pytest.mark.skipif(
    True,
    reason="Migration tests require Postgres. Run in Docker: docker compose exec backend bash -lc 'cd backend && uv run pytest tests/test_alembic_migrations.py'",
)
def test_0004_order_index_is_btree() -> None:
    """Index should use btree (Postgres default)."""
    engine = _ensure_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT indexdef FROM pg_indexes "
                "WHERE tablename = 'rag_contextitem' "
                "AND indexname = 'ix_rag_contextitem_order_index'"
            )
        ).fetchone()
        assert result is not None
        indexdef = result[0]
        assert "btree" in indexdef.lower()
