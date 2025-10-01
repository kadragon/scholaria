"""Tests for Alembic configuration (Phase 1 setup)."""

import importlib.util
from pathlib import Path

from alembic.config import Config


def test_alembic_ini_exists() -> None:
    """Alembic configuration file should exist at project root."""
    assert Path("alembic.ini").exists()


def test_alembic_metadata_includes_topic_table() -> None:
    """Alembic env must expose SQLAlchemy metadata with rag_topic table."""
    cfg = Config("alembic.ini")
    script_location = cfg.get_main_option("script_location")
    assert script_location == "alembic"

    env_path = Path("alembic/env.py")
    assert env_path.exists()

    spec = importlib.util.spec_from_file_location("alembic_env", env_path)
    assert spec is not None
    assert spec.loader is not None
    env_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(env_module)
    metadata = getattr(env_module, "target_metadata", None)
    assert metadata is not None
    assert "rag_topic" in metadata.tables
