from .settings import *

# Override database settings for testing
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}


# Disable migrations for faster tests
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

# Test-specific RAG configuration
QDRANT_COLLECTION_NAME = "context_items"
OPENAI_EMBEDDING_DIM = 4  # Use smaller dimension for faster tests

# Disable OpenAI API for unit tests (set to None to skip integration tests)
OPENAI_API_KEY = None

# Test-specific logging to reduce noise
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["null"],
    },
}

# Email backend for testing
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
