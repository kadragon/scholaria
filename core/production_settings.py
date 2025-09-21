"""
Production settings for Scholaria RAG System.

This module extends the base settings with production-specific configurations
including security, performance, and deployment optimizations.
"""

import os
from typing import Any

from .settings import *

# Security Configuration
DEBUG = False
SECRET_KEY = os.getenv("SECRET_KEY") or ""

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required in production")

# Allowed hosts from environment
ALLOWED_HOSTS = [
    host.strip() for host in os.getenv("ALLOWED_HOSTS", "").split(",") if host.strip()
]

if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS environment variable is required in production")

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# SSL/HTTPS Configuration (when behind load balancer/proxy)
if os.getenv("SECURE_SSL_REDIRECT", "False").lower() == "true":
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = (
        tuple(os.getenv("SECURE_PROXY_SSL_HEADER", "").split(","))
        if os.getenv("SECURE_PROXY_SSL_HEADER")
        else None
    )
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Proxy Configuration
if os.getenv("USE_X_FORWARDED_HOST", "False").lower() == "true":
    USE_X_FORWARDED_HOST = True

if os.getenv("USE_X_FORWARDED_PORT", "False").lower() == "true":
    USE_X_FORWARDED_PORT = True

# Session Security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# CSRF Security
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_AGE = 3600  # 1 hour

# Database Configuration with Connection Pooling
_db_config: dict[str, Any] = DATABASES["default"]
_db_config.update(
    {
        "CONN_MAX_AGE": 600,  # 10 minutes
        "CONN_HEALTH_CHECKS": True,
    }
)
DATABASES["default"] = _db_config

# Cache Configuration with longer timeouts
_cache_config: dict[str, Any] = CACHES["default"]
_cache_config.update(
    {
        "TIMEOUT": 300,  # 5 minutes default
    }
)
CACHES["default"] = _cache_config

# Email Configuration for Error Reporting
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"
)

if EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend":
    EMAIL_HOST = os.getenv("EMAIL_HOST")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@scholaria.local")
SERVER_EMAIL = os.getenv("SERVER_EMAIL", "server@scholaria.local")

# Admin Configuration
ADMINS = [("Scholaria Admin", os.getenv("ADMIN_EMAIL", "admin@scholaria.local"))]
MANAGERS = ADMINS

# Logging Configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/app/logs/django.log",
            "maxBytes": 1024 * 1024 * 50,  # 50MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/app/logs/django_error.log",
            "maxBytes": 1024 * 1024 * 50,  # 50MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": True,
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["error_file", "mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "rag": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "celery": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Static Files Configuration - use manifest storage for cache busting
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# Performance Optimizations
MIDDLEWARE.insert(1, "django.middleware.cache.UpdateCacheMiddleware")
MIDDLEWARE.append("django.middleware.cache.FetchFromCacheMiddleware")

# Cache entire site for anonymous users
CACHE_MIDDLEWARE_ALIAS = "default"
CACHE_MIDDLEWARE_SECONDS = 600  # 10 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = "scholaria"

# REST Framework Production Settings
REST_FRAMEWORK.update(
    {
        "DEFAULT_RENDERER_CLASSES": [
            "rest_framework.renderers.JSONRenderer",
        ],
        "DEFAULT_THROTTLE_RATES": {
            "anon": "100/hour",
            "user": "1000/hour",
            "rag_questions": "30/min",
        },
    }
)

# Celery Production Configuration
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_DISABLE_RATE_LIMITS = False

# Monitoring Configuration
if os.getenv("SENTRY_DSN"):
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[
            DjangoIntegration(
                transaction_style="url",
                middleware_spans=True,
                signals_spans=True,
                cache_spans=True,
            ),
            CeleryIntegration(
                monitor_beat_tasks=True,
                propagate_traces=True,
            ),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment="production",
    )

# Health Check Configuration
HEALTH_CHECK_ACCESS_TOKEN = os.getenv("HEALTH_CHECK_ACCESS_TOKEN")

# File Upload Security
DATA_UPLOAD_MAX_MEMORY_SIZE = FILE_VALIDATION_MAX_SIZE
FILE_UPLOAD_MAX_MEMORY_SIZE = FILE_VALIDATION_MAX_SIZE

# Admin URL (should be changed from default in production)
ADMIN_URL_PATH = os.getenv("ADMIN_URL_PATH", "admin")

# OpenAI Production Limits
OPENAI_RATE_LIMIT_REQUESTS_PER_MINUTE = int(
    os.getenv("OPENAI_RATE_LIMIT_REQUESTS_PER_MINUTE", "3000")
)
OPENAI_RATE_LIMIT_TOKENS_PER_MINUTE = int(
    os.getenv("OPENAI_RATE_LIMIT_TOKENS_PER_MINUTE", "250000")
)
