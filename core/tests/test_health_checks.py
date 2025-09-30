"""
Tests for comprehensive health check endpoints.
"""

from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.health import (
    CacheHealthCheck,
    DatabaseHealthCheck,
    ExternalServiceHealthCheck,
    HealthChecker,
)


class HealthCheckerTest(TestCase):
    """Test the HealthChecker utility class."""

    def setUp(self):
        """Set up test environment."""
        self.health_checker = HealthChecker()

    def test_health_checker_initialization(self):
        """Test that HealthChecker initializes correctly."""
        self.assertIsInstance(self.health_checker, HealthChecker)
        self.assertEqual(len(self.health_checker.checks), 0)

    def test_add_health_check(self):
        """Test adding health checks to the checker."""
        db_check = DatabaseHealthCheck()
        self.health_checker.add_check("database", db_check)

        self.assertEqual(len(self.health_checker.checks), 1)
        self.assertIn("database", self.health_checker.checks)

    def test_run_all_checks_success(self):
        """Test running all health checks when everything is healthy."""
        mock_check = MagicMock()
        mock_check.check.return_value = {"status": "healthy", "message": "OK"}

        self.health_checker.add_check("test", mock_check)
        results = self.health_checker.run_all_checks()

        self.assertEqual(results["overall_status"], "healthy")
        self.assertIn("test", results["checks"])
        self.assertEqual(results["checks"]["test"]["status"], "healthy")

    def test_run_all_checks_failure(self):
        """Test running all health checks when some are unhealthy."""
        healthy_check = MagicMock()
        healthy_check.check.return_value = {"status": "healthy", "message": "OK"}

        unhealthy_check = MagicMock()
        unhealthy_check.check.return_value = {
            "status": "unhealthy",
            "message": "Connection failed",
        }

        self.health_checker.add_check("healthy", healthy_check)
        self.health_checker.add_check("unhealthy", unhealthy_check)

        results = self.health_checker.run_all_checks()

        self.assertEqual(results["overall_status"], "unhealthy")
        self.assertEqual(results["checks"]["healthy"]["status"], "healthy")
        self.assertEqual(results["checks"]["unhealthy"]["status"], "unhealthy")


class DatabaseHealthCheckTest(TestCase):
    """Test database health check functionality."""

    def setUp(self):
        """Set up test environment."""
        self.db_check = DatabaseHealthCheck()

    def test_database_check_success(self):
        """Test successful database connection check."""
        result = self.db_check.check()

        self.assertEqual(result["status"], "healthy")
        self.assertIn("message", result)
        self.assertIn("response_time_ms", result)
        self.assertIsInstance(result["response_time_ms"], (int, float))

    @patch("django.db.connection.cursor")
    def test_database_check_failure(self, mock_cursor):
        """Test database connection failure."""
        mock_cursor.side_effect = Exception("Connection failed")

        result = self.db_check.check()

        self.assertEqual(result["status"], "unhealthy")
        self.assertIn("error", result)


class CacheHealthCheckTest(TestCase):
    """Test cache health check functionality."""

    def setUp(self):
        """Set up test environment."""
        self.cache_check = CacheHealthCheck()

    def test_cache_check_success(self):
        """Test successful cache operation check."""
        result = self.cache_check.check()

        self.assertEqual(result["status"], "healthy")
        self.assertIn("message", result)
        self.assertIn("response_time_ms", result)

    @patch("django.core.cache.cache.set")
    def test_cache_check_failure(self, mock_cache_set):
        """Test cache operation failure."""
        mock_cache_set.side_effect = Exception("Cache unavailable")

        result = self.cache_check.check()

        self.assertEqual(result["status"], "unhealthy")
        self.assertIn("error", result)


class ExternalServiceHealthCheckTest(TestCase):
    """Test external service health check functionality."""

    def setUp(self):
        """Set up test environment."""
        self.qdrant_check = ExternalServiceHealthCheck(
            name="Qdrant", url="http://localhost:6333/health", timeout=5
        )

    @patch("requests.get")
    def test_external_service_check_success(self, mock_get):
        """Test successful external service check."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_get.return_value = mock_response

        result = self.qdrant_check.check()

        self.assertEqual(result["status"], "healthy")
        self.assertIn("response_time_ms", result)

    @patch("requests.get")
    def test_external_service_check_failure(self, mock_get):
        """Test external service connection failure."""
        mock_get.side_effect = Exception("Connection refused")

        result = self.qdrant_check.check()

        self.assertEqual(result["status"], "unhealthy")
        self.assertIn("error", result)


class HealthCheckAPITest(APITestCase):
    """Test health check API endpoints."""

    def setUp(self):
        """Set up test environment."""
        self.health_url = reverse("health-check")
        self.detailed_health_url = reverse("health-check-detailed")

    @patch("core.health.CacheHealthCheck.check")
    @patch("core.health.DatabaseHealthCheck.check")
    def test_basic_health_check_endpoint(self, mock_db_check, mock_cache_check):
        """Test basic health check endpoint returns 200."""
        mock_db_check.return_value = {"status": "healthy"}
        mock_cache_check.return_value = {"status": "healthy"}

        response = self.client.get(self.health_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("status", data)

    @patch("core.health.get_default_health_checker")
    def test_detailed_health_check_endpoint(self, mock_get_checker):
        """Test detailed health check endpoint returns comprehensive info."""
        mock_checker = MagicMock()
        mock_checker.run_all_checks.return_value = {
            "overall_status": "healthy",
            "checks": {
                "database": {"status": "healthy"},
                "cache": {"status": "healthy"},
            },
            "timestamp": "2025-09-30T09:00:00Z",
            "version": "1.0.0",
        }
        mock_get_checker.return_value = mock_checker

        response = self.client.get(self.detailed_health_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Check required fields
        self.assertIn("overall_status", data)
        self.assertIn("checks", data)
        self.assertIn("timestamp", data)
        self.assertIn("version", data)

        # Check that we have essential checks
        checks = data["checks"]
        self.assertIn("database", checks)
        self.assertIn("cache", checks)

    @patch("core.health.CacheHealthCheck.check")
    @patch("core.health.DatabaseHealthCheck.check")
    def test_health_check_with_access_token(self, mock_db_check, mock_cache_check):
        """Test health check endpoint with access token protection."""
        mock_db_check.return_value = {"status": "healthy"}
        mock_cache_check.return_value = {"status": "healthy"}

        # Test without token (should work for basic endpoint)
        response = self.client.get(self.health_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("core.health.HealthChecker.run_all_checks")
    def test_health_check_unhealthy_response(self, mock_run_checks):
        """Test health check returns 503 when services are unhealthy."""
        mock_run_checks.return_value = {
            "overall_status": "unhealthy",
            "checks": {
                "database": {"status": "unhealthy", "error": "Connection failed"}
            },
        }

        response = self.client.get(self.detailed_health_url)

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        data = response.json()
        self.assertEqual(data["overall_status"], "unhealthy")

    @patch("core.health.get_default_health_checker")
    def test_health_check_response_format(self, mock_get_checker):
        """Test that health check response has correct format."""
        mock_checker = MagicMock()
        mock_checker.run_all_checks.return_value = {
            "overall_status": "healthy",
            "checks": {
                "database": {"status": "healthy", "response_time_ms": 10},
                "cache": {"status": "healthy", "response_time_ms": 5},
            },
            "timestamp": "2025-09-30T09:00:00Z",
            "version": "1.0.0",
        }
        mock_get_checker.return_value = mock_checker

        response = self.client.get(self.detailed_health_url)
        data = response.json()

        # Validate overall structure
        required_fields = ["overall_status", "checks", "timestamp", "version"]
        for field in required_fields:
            self.assertIn(field, data)

        # Validate individual check format
        for _check_name, check_result in data["checks"].items():
            self.assertIn("status", check_result)
            self.assertIn(check_result["status"], ["healthy", "unhealthy"])

            if check_result["status"] == "healthy":
                self.assertIn("response_time_ms", check_result)
            else:
                self.assertIn("error", check_result)

    def test_health_check_performance_metrics(self):
        """Test that health check includes performance metrics."""
        response = self.client.get(self.detailed_health_url)
        data = response.json()

        # Check for performance metrics
        for _check_name, check_result in data["checks"].items():
            if check_result["status"] == "healthy":
                self.assertIn("response_time_ms", check_result)
                self.assertIsInstance(check_result["response_time_ms"], (int, float))
                self.assertGreaterEqual(check_result["response_time_ms"], 0)
