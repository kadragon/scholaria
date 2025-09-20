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

# Enable local caching for LlamaIndex-backed utilities during tests
LLAMAINDEX_CACHE_ENABLED = True
LLAMAINDEX_CACHE_DIR = BASE_DIR / "tmp" / "llamaindex_cache"
LLAMAINDEX_CACHE_NAMESPACE = "scholaria-test"

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

# Disable rate limiting for tests
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "10000/hour",
        "user": "10000/hour",
        "rag_questions": "10000/hour",
    },
}
