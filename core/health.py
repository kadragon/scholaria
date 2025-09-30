"""
Comprehensive health check system for Scholaria.

This module provides a flexible health check framework that can monitor
various system components including databases, caches, and external services.
"""

import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

import requests
from django.conf import settings
from django.core.cache import cache
from django.db import connection


class BaseHealthCheck(ABC):
    """
    Abstract base class for health checks.

    All health check implementations should inherit from this class
    and implement the check() method.
    """

    @abstractmethod
    def check(self) -> dict[str, Any]:
        """
        Perform the health check.

        Returns:
            Dictionary containing health check results with at least:
            - status: "healthy" or "unhealthy"
            - message: Human readable status message
            - response_time_ms: Time taken for the check (if successful)
            - error: Error message (if unsuccessful)
        """
        pass


class DatabaseHealthCheck(BaseHealthCheck):
    """
    Health check for database connectivity and basic operations.

    This check verifies that the database connection is working
    and can perform basic read operations.
    """

    def check(self) -> dict[str, Any]:
        """
        Check database connectivity.

        Returns:
            Health check result dictionary
        """
        start_time = time.time()

        try:
            # Test basic database connectivity
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

            if result and result[0] == 1:
                response_time = round((time.time() - start_time) * 1000, 2)
                return {
                    "status": "healthy",
                    "message": "Database connection successful",
                    "response_time_ms": response_time,
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": "Database query returned unexpected result",
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": f"Database connection failed: {str(e)}",
            }


class CacheHealthCheck(BaseHealthCheck):
    """
    Health check for cache system (Redis) connectivity and operations.

    This check verifies that the cache backend is working
    and can perform basic read/write operations.
    """

    def check(self) -> dict[str, Any]:
        """
        Check cache connectivity and operations.

        Returns:
            Health check result dictionary
        """
        start_time = time.time()
        test_key = f"health_check_{int(time.time())}"
        test_value = "health_check_value"

        try:
            # Test cache write operation
            cache.set(test_key, test_value, timeout=30)

            # Test cache read operation
            retrieved_value = cache.get(test_key)

            # Clean up test data
            cache.delete(test_key)

            if retrieved_value == test_value:
                response_time = round((time.time() - start_time) * 1000, 2)
                return {
                    "status": "healthy",
                    "message": "Cache operations successful",
                    "response_time_ms": response_time,
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": "Cache read/write operations failed",
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": f"Cache operation failed: {str(e)}",
            }


class ExternalServiceHealthCheck(BaseHealthCheck):
    """
    Health check for external service connectivity.

    This check verifies that external services (like Qdrant, OpenAI API)
    are accessible and responding correctly.
    """

    def __init__(
        self,
        name: str,
        url: str,
        timeout: int = 10,
        headers: dict[str, str] | None = None,
    ):
        """
        Initialize external service health check.

        Args:
            name: Human readable name of the service
            url: Health check URL for the service
            timeout: Request timeout in seconds
            headers: Optional HTTP headers for the request
        """
        self.name = name
        self.url = url
        self.timeout = timeout
        self.headers = headers or {}

    def check(self) -> dict[str, Any]:
        """
        Check external service connectivity.

        Returns:
            Health check result dictionary
        """
        start_time = time.time()

        try:
            response = requests.get(
                self.url, timeout=self.timeout, headers=self.headers
            )

            response_time = round((time.time() - start_time) * 1000, 2)

            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "message": f"{self.name} service accessible",
                    "response_time_ms": response_time,
                    "status_code": response.status_code,
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"{self.name} returned status {response.status_code}",
                    "status_code": response.status_code,
                }

        except requests.exceptions.Timeout:
            return {
                "status": "unhealthy",
                "error": f"{self.name} service timeout after {self.timeout}s",
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "unhealthy",
                "error": f"{self.name} service connection refused",
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": f"{self.name} service check failed: {str(e)}",
            }


class HealthChecker:
    """
    Main health checker that orchestrates multiple health checks.

    This class manages a collection of health checks and provides
    methods to run them individually or all at once.
    """

    def __init__(self) -> None:
        """Initialize the health checker."""
        self.checks: dict[str, BaseHealthCheck] = {}

    def add_check(self, name: str, health_check: BaseHealthCheck) -> None:
        """
        Add a health check to the checker.

        Args:
            name: Unique name for the health check
            health_check: Health check instance
        """
        self.checks[name] = health_check

    def run_check(self, name: str) -> dict[str, Any]:
        """
        Run a specific health check by name.

        Args:
            name: Name of the health check to run

        Returns:
            Health check result dictionary

        Raises:
            KeyError: If health check name is not found
        """
        if name not in self.checks:
            raise KeyError(f"Health check '{name}' not found")

        return self.checks[name].check()

    def run_all_checks(self) -> dict[str, Any]:
        """
        Run all registered health checks.

        Returns:
            Dictionary containing overall status and individual check results
        """
        results: dict[str, Any] = {
            "overall_status": "healthy",
            "checks": {},
            "timestamp": datetime.utcnow().isoformat(),
            "version": getattr(settings, "VERSION", "1.0.0"),
        }

        # Run all checks
        for name, health_check in self.checks.items():
            try:
                check_result = health_check.check()
                results["checks"][name] = check_result

                # If any check is unhealthy, mark overall status as unhealthy
                if check_result["status"] == "unhealthy":
                    results["overall_status"] = "unhealthy"

            except Exception as e:
                # If a check raises an exception, mark it as unhealthy
                results["checks"][name] = {
                    "status": "unhealthy",
                    "error": f"Health check failed with exception: {str(e)}",
                }
                results["overall_status"] = "unhealthy"

        return results


def get_default_health_checker() -> HealthChecker:
    """
    Get a health checker with default checks configured.

    Returns:
        HealthChecker instance with standard checks configured
    """
    checker = HealthChecker()

    # Add database check
    checker.add_check("database", DatabaseHealthCheck())

    # Add cache check
    checker.add_check("cache", CacheHealthCheck())

    # Add external service checks based on configuration
    # Only add external service checks if not in test mode
    if not getattr(settings, "TESTING", False):
        if hasattr(settings, "QDRANT_HOST") and settings.QDRANT_HOST:
            qdrant_port = getattr(settings, "QDRANT_PORT", 6333)
            qdrant_url = f"http://{settings.QDRANT_HOST}:{qdrant_port}/health"
            checker.add_check(
                "qdrant", ExternalServiceHealthCheck("Qdrant", qdrant_url)
            )

        # Add OpenAI API check if API key is configured
        if hasattr(settings, "OPENAI_API_KEY") and settings.OPENAI_API_KEY:
            openai_headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
            checker.add_check(
                "openai",
                ExternalServiceHealthCheck(
                    "OpenAI API",
                    "https://api.openai.com/v1/models",
                    headers=openai_headers,
                    timeout=10,
                ),
            )

    return checker
