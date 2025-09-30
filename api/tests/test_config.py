"""Tests for FastAPI settings helpers."""

import importlib
from pathlib import Path

import pytest
from django.test.utils import override_settings

import api.config as config_module


@pytest.fixture(autouse=True)
def reset_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clear database-related env vars before each test."""
    for key in (
        "DATABASE_URL",
        "DB_ENGINE",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
        "DB_HOST",
        "DB_PORT",
        "JWT_SECRET_KEY",
        "JWT_ALGORITHM",
        "JWT_ACCESS_TOKEN_EXPIRE_HOURS",
    ):
        monkeypatch.delenv(key, raising=False)


def test_database_config_uses_sqlite_when_engine_is_sqlite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """database_config should construct sqlite URL when DB_ENGINE indicates sqlite."""
    monkeypatch.setenv("DB_ENGINE", "django.db.backends.sqlite3")
    sqlite_path = tmp_path / "test.sqlite3"
    monkeypatch.setenv("DB_NAME", str(sqlite_path))

    with override_settings(
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": str(sqlite_path),
            }
        }
    ):
        module = importlib.reload(config_module)
        settings = module.Settings()

        database_url, connect_args = settings.database_config()

        assert database_url == f"sqlite+pysqlite:///{sqlite_path}"
        assert connect_args.get("check_same_thread") is False

    # Restore module to original configuration after override
    importlib.reload(config_module)


def test_jwt_settings_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings should expose JWT configuration sourced from env vars."""

    monkeypatch.setenv("JWT_SECRET_KEY", "unit-test-secret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS384")
    monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRE_HOURS", "8")

    module = importlib.reload(config_module)
    settings = module.Settings()

    assert settings.JWT_SECRET_KEY == "unit-test-secret"
    assert settings.JWT_ALGORITHM == "HS384"
    assert settings.JWT_ACCESS_TOKEN_EXPIRE_HOURS == 8

    importlib.reload(config_module)
