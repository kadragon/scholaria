"""Alembic environment configuration for FastAPI migrations."""

from __future__ import annotations

import logging
from logging.config import fileConfig
from typing import Literal

from sqlalchemy import engine_from_config, pool
from sqlalchemy.schema import SchemaItem

from alembic import context
from alembic.config import Config
from api.config import settings
from api.models import (
    associations,  # noqa: F401
    topic,  # noqa: F401
)
from api.models import context as context_models  # noqa: F401
from api.models.base import Base

logger = logging.getLogger(__name__)

if not hasattr(context, "config") or context.config is None:
    context.config = Config("alembic.ini")

config = context.config
# Propagate runtime database URL into alembic.ini placeholders.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
config.set_main_option("database_url", settings.DATABASE_URL)

if config.config_file_name:
    fileConfig(config.config_file_name)

# Target metadata for 'autogenerate' support.
target_metadata = Base.metadata


def include_object(
    object_: SchemaItem,
    name: str | None,
    type_: Literal[
        "schema",
        "table",
        "column",
        "index",
        "unique_constraint",
        "foreign_key_constraint",
    ],
    reflected: bool,
    compare_to: SchemaItem | None,
) -> bool:
    """Exclude Alembic-internal tables we do not manage."""
    if type_ == "table" and name in {"alembic_version", "django_migrations"}:
        return False
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        include_object=include_object,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    section = config.get_section(config.config_ini_section) or {}
    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if getattr(config, "cmd_opts", None):
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
