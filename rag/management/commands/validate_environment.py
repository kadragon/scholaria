"""
Django management command to validate environment configuration.
"""

from typing import Any
from urllib.parse import urlparse

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Validate environment configuration for Scholaria RAG system"

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--check-services",
            action="store_true",
            help="Check if external services are reachable",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write(
            self.style.SUCCESS("🔍 Validating Scholaria Environment Configuration")
        )
        self.stdout.write("=" * 60)

        errors = []
        warnings = []

        # Validate critical environment variables
        errors.extend(self._validate_critical_vars())
        warnings.extend(self._validate_security_settings())
        warnings.extend(self._validate_production_readiness())

        # Check service connectivity if requested
        if options["check_services"]:
            errors.extend(self._check_service_connectivity())

        # Display results
        self._display_results(errors, warnings)

        if errors:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Validation failed with {len(errors)} error(s)")
            )
        else:
            self.stdout.write(self.style.SUCCESS("\n✅ Environment validation passed!"))
            if warnings:
                self.stdout.write(
                    self.style.WARNING(
                        f"Found {len(warnings)} warning(s) - review recommended"
                    )
                )

    def _validate_critical_vars(self) -> list[str]:
        """Validate critical environment variables."""
        errors = []

        # OpenAI API Key
        if not settings.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required for AI functionality")
        elif settings.OPENAI_API_KEY == "your_openai_api_key_here":
            errors.append("OPENAI_API_KEY contains placeholder value")

        # Database configuration
        db_config = settings.DATABASES["default"]
        if not db_config.get("PASSWORD") and not settings.DEBUG:
            errors.append("Database password is required in production")

        # Secret key
        if (
            settings.SECRET_KEY
            == "django-insecure-f+=br0u!^3%$^^^3(iodi37msa-*8@zo3q7tb%73^5&v4lbo(l"
        ):
            errors.append("SECRET_KEY is using default insecure value")

        return errors

    def _validate_security_settings(self) -> list[str]:
        """Validate security-related settings."""
        warnings = []

        if settings.DEBUG and not settings.ALLOWED_HOSTS:
            warnings.append("ALLOWED_HOSTS should be configured even in development")

        if not settings.DEBUG:
            # Production security checks
            if not hasattr(settings, "SECURE_SSL_REDIRECT"):
                warnings.append("SECURE_SSL_REDIRECT not configured for production")

            if settings.MINIO_ACCESS_KEY == "minioadmin":
                warnings.append(
                    "MinIO using default credentials - change for production"
                )

        return warnings

    def _validate_production_readiness(self) -> list[str]:
        """Check production readiness."""
        warnings = []

        if not settings.DEBUG:
            # Check if using production-appropriate settings
            if settings.QDRANT_COLLECTION_NAME == "scholaria_documents":
                warnings.append("Consider using production-specific collection name")

            if settings.LLAMAINDEX_CACHE_NAMESPACE == "scholaria-default":
                warnings.append("Consider using production-specific cache namespace")

        return warnings

    def _check_service_connectivity(self) -> list[str]:
        """Check if external services are reachable."""
        errors = []

        self.stdout.write("\n🔌 Checking service connectivity...")

        # Check Redis
        try:
            import redis

            redis_url = urlparse(settings.REDIS_URL)
            r = redis.Redis(
                host=redis_url.hostname or "localhost",
                port=redis_url.port or 6379,
                decode_responses=True,
            )
            r.ping()
            self.stdout.write("  ✅ Redis connection successful")
        except Exception as e:
            errors.append(f"Redis connection failed: {e}")

        # Check Qdrant
        try:
            import httpx

            response = httpx.get(
                f"http://{settings.QDRANT_HOST}:{settings.QDRANT_PORT}/health",
                timeout=5.0,
            )
            if response.status_code == 200:
                self.stdout.write("  ✅ Qdrant connection successful")
            else:
                errors.append(f"Qdrant health check failed: {response.status_code}")
        except Exception as e:
            errors.append(f"Qdrant connection failed: {e}")

        # Check database
        try:
            from django.db import connection

            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write("  ✅ Database connection successful")
        except Exception as e:
            errors.append(f"Database connection failed: {e}")

        return errors

    def _display_results(self, errors: list[str], warnings: list[str]) -> None:
        """Display validation results."""
        if errors:
            self.stdout.write(self.style.ERROR("\n❌ ERRORS:"))
            for error in errors:
                self.stdout.write(f"  • {error}")

        if warnings:
            self.stdout.write(self.style.WARNING("\n⚠️  WARNINGS:"))
            for warning in warnings:
                self.stdout.write(f"  • {warning}")

        # Display current configuration summary
        self.stdout.write(self.style.HTTP_INFO("\n📋 CONFIGURATION SUMMARY:"))
        self.stdout.write(
            f"  • Environment: {'Production' if not settings.DEBUG else 'Development'}"
        )
        self.stdout.write(
            f"  • Database: {settings.DATABASES['default']['ENGINE'].split('.')[-1]}"
        )
        self.stdout.write(f"  • Time Zone: {settings.TIME_ZONE}")
        self.stdout.write(f"  • Language: {settings.LANGUAGE_CODE}")
        self.stdout.write(f"  • OpenAI Model: {settings.OPENAI_CHAT_MODEL}")
        self.stdout.write(f"  • Embedding Model: {settings.OPENAI_EMBEDDING_MODEL}")
        self.stdout.write(f"  • Cache Enabled: {settings.LLAMAINDEX_CACHE_ENABLED}")
