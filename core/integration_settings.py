"""
Integration test settings for external API testing.

This configuration is used when running integration tests that require
real API keys and external service connections.
"""

import os

# Import all settings from base settings
from .settings import *

# Use SQLite for faster integration tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Integration test specific configurations
QDRANT_COLLECTION_NAME = "integration_test_items"
OPENAI_EMBEDDING_DIM = 3072  # Use production dimensions

# Require real API keys for integration tests
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError(
        "OPENAI_API_KEY environment variable is required for integration tests. "
        "Set it before running: OPENAI_API_KEY=your_key python manage.py test --settings=core.integration_settings"
    )

# Use real API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# Disable migrations for faster test execution
class DisableMigrations:
    def __contains__(self, item: str) -> bool:
        return True

    def __getitem__(self, item: str) -> None:
        return None


MIGRATION_MODULES = DisableMigrations()

# Faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Test-specific logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "rag": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
