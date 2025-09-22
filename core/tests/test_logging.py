"""
Tests for logging and monitoring functionality.
"""

import json
import logging
from unittest.mock import MagicMock

from django.contrib.auth.models import User
from django.test import TestCase

from core.logging import (
    JSONFormatter,
    RequestLoggingMiddleware,
    StructuredLoggerAdapter,
)


class StructuredLoggingTest(TestCase):
    """Test structured logging functionality."""

    def setUp(self):
        """Set up test environment."""
        self.logger = logging.getLogger("test_logger")
        self.adapter = StructuredLoggerAdapter(self.logger, {})

    def test_structured_log_format(self):
        """Test that structured logs are properly formatted."""
        # Test the process method directly
        msg, kwargs = self.adapter.process(
            "Test message",
            {"extra": {"user_id": 123, "action": "test_action", "duration_ms": 150}},
        )

        self.assertEqual(msg, "Test message")
        self.assertIn("user_id", kwargs["extra"])
        self.assertIn("action", kwargs["extra"])
        self.assertIn("duration_ms", kwargs["extra"])
        self.assertEqual(kwargs["extra"]["user_id"], 123)

    def test_json_serializable_logs(self):
        """Test that log entries are JSON serializable."""
        log_data = {
            "message": "Test message",
            "user_id": 123,
            "timestamp": "2023-01-01T00:00:00Z",
            "level": "INFO",
        }

        # Should not raise an exception
        json_string = json.dumps(log_data)
        self.assertIsInstance(json_string, str)

        # Should be deserializable
        parsed_data = json.loads(json_string)
        self.assertEqual(parsed_data["message"], "Test message")
        self.assertEqual(parsed_data["user_id"], 123)


class RequestLoggingMiddlewareTest(TestCase):
    """Test request logging middleware."""

    def setUp(self):
        """Set up test environment."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_request_logging_middleware_creation(self):
        """Test that RequestLoggingMiddleware can be created."""
        middleware = RequestLoggingMiddleware(lambda req: None)  # type: ignore[arg-type]
        self.assertIsInstance(middleware, RequestLoggingMiddleware)

    def test_get_client_ip(self):
        """Test client IP extraction."""
        middleware = RequestLoggingMiddleware(lambda req: None)  # type: ignore[arg-type]

        # Create a mock request
        request = MagicMock()
        request.META = {"REMOTE_ADDR": "192.168.1.1"}

        ip = middleware._get_client_ip(request)
        self.assertEqual(ip, "192.168.1.1")

        # Test with X-Forwarded-For header
        request.META = {
            "HTTP_X_FORWARDED_FOR": "10.0.0.1, 192.168.1.1",
            "REMOTE_ADDR": "192.168.1.1",
        }

        ip = middleware._get_client_ip(request)
        self.assertEqual(ip, "10.0.0.1")

    def test_json_formatter(self):
        """Test JSON formatter functionality."""
        formatter = JSONFormatter()

        # Create a log record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=123,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Add extra attributes
        record.user_id = 456
        record.duration_ms = 250.5

        formatted = formatter.format(record)

        # Should be valid JSON
        data = json.loads(formatted)
        self.assertEqual(data["message"], "Test message")
        self.assertEqual(data["level"], "INFO")
        self.assertEqual(data["user_id"], 456)
        self.assertEqual(data["duration_ms"], 250.5)


class LogAggregationTest(TestCase):
    """Test log aggregation functionality."""

    def test_error_log_contains_required_fields(self):
        """Test that error logs contain all required fields for aggregation."""
        logger = logging.getLogger("test_error_logger")
        adapter = StructuredLoggerAdapter(logger, {})

        # Test the process method directly
        msg, kwargs = adapter.process(
            "Database connection failed",
            {
                "extra": {
                    "error_type": "DatabaseError",
                    "component": "rag.storage",
                    "severity": "high",
                    "user_id": 123,
                }
            },
        )

        extra = kwargs["extra"]

        # Required fields for log aggregation
        required_fields = ["error_type", "component", "severity"]
        for field in required_fields:
            self.assertIn(field, extra)

    def test_performance_log_format(self):
        """Test that performance logs are properly formatted."""
        logger = logging.getLogger("test_perf_logger")
        adapter = StructuredLoggerAdapter(logger, {})

        # Test the process method directly
        msg, kwargs = adapter.process(
            "Query executed",
            {
                "extra": {
                    "operation": "search",
                    "duration_ms": 250,
                    "result_count": 5,
                    "cache_hit": False,
                }
            },
        )

        extra = kwargs["extra"]

        # Performance monitoring fields
        perf_fields = ["operation", "duration_ms"]
        for field in perf_fields:
            self.assertIn(field, extra)
