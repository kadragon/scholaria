"""Tests for Alembic configuration (Phase 1 setup)."""

import importlib.util
import os
from pathlib import Path

from alembic.config import Config

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
ALEMBIC_INI = BACKEND_ROOT / "alembic.ini"
ALEMBIC_SCRIPT = BACKEND_ROOT / "alembic" / "env.py"


def test_alembic_ini_exists() -> None:
    """Alembic configuration file should exist at backend root."""
    assert ALEMBIC_INI.exists()


def test_alembic_metadata_includes_topic_table() -> None:
    """Alembic env must expose SQLAlchemy metadata with rag_topic table."""
    cfg = Config(str(ALEMBIC_INI))
    script_location = cfg.get_main_option("script_location")
    assert script_location == "alembic"

    assert ALEMBIC_SCRIPT.exists()

    cwd = os.getcwd()
    os.chdir(BACKEND_ROOT)
    spec = importlib.util.spec_from_file_location("alembic_env", ALEMBIC_SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    env_module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(env_module)
    finally:
        os.chdir(cwd)
    metadata = getattr(env_module, "target_metadata", None)
    assert metadata is not None
    assert "rag_topic" in metadata.tables
