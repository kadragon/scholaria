"""
Structured logging and monitoring utilities for Scholaria.
"""

import json
import logging
import time
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class StructuredLoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that adds structured data to log records.

    This adapter ensures that log entries contain structured data
    that can be easily parsed by log aggregation systems.
    """

    def __init__(self, logger: logging.Logger, extra: dict[str, Any]):
        """Initialize the adapter with a logger and extra data."""
        super().__init__(logger, extra)

    def process(self, msg: str, kwargs: dict[str, Any]) -> tuple[str, dict[str, Any]]:  # type: ignore[override]
        """
        Process the log record by adding structured data.

        Args:
            msg: The log message
            kwargs: Additional keyword arguments

        Returns:
            Tuple of processed message and kwargs
        """
        if "extra" not in kwargs:
            kwargs["extra"] = {}

        # Merge adapter extra data with record extra data
        kwargs["extra"].update(self.extra)

        # Ensure all extra data is JSON serializable
        kwargs["extra"] = self._make_json_serializable(kwargs["extra"])

        return msg, kwargs

    def _make_json_serializable(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Ensure all data in the dictionary is JSON serializable.

        Args:
            data: Dictionary to process

        Returns:
            Dictionary with JSON serializable values
        """
        serializable_data = {}
        for key, value in data.items():
            try:
                json.dumps(value)
                serializable_data[key] = value
            except (TypeError, ValueError):
                # Convert non-serializable objects to string
                serializable_data[key] = str(value)

        return serializable_data


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware that logs HTTP requests with structured data.

    This middleware logs all HTTP requests including user information,
    request details, response status, and processing time.
    """

    def process_request(self, request: HttpRequest) -> None:
        """
        Process the incoming request.

        Args:
            request: The HTTP request object
        """
        request._logging_start_time = time.time()  # type: ignore[attr-defined]

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """
        Process the outgoing response and log request details.

        Args:
            request: The HTTP request object
            response: The HTTP response object

        Returns:
            The unmodified response
        """
        # Calculate request duration
        start_time = getattr(request, "_logging_start_time", time.time())
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Get user information
        user_id = None
        if hasattr(request, "user") and request.user.is_authenticated:
            user_id = request.user.id

        # Create structured log data
        log_data = {
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "user_id": user_id,
            "duration_ms": duration_ms,
            "user_agent": request.headers.get("user-agent", ""),
            "remote_addr": self._get_client_ip(request),
        }

        # Log the request
        adapter = StructuredLoggerAdapter(logger, log_data)
        adapter.info(f"{request.method} {request.path} - {response.status_code}")

        return response

    def _get_client_ip(self, request: HttpRequest) -> str:
        """
        Get the client IP address from the request.

        Args:
            request: The HTTP request object

        Returns:
            The client IP address
        """
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "")
        return ip


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.

    This formatter outputs log records as JSON objects,
    making them easy to parse by log aggregation systems.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as JSON.

        Args:
            record: The log record to format

        Returns:
            JSON formatted log string
        """
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra data if present
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        if hasattr(record, "method"):
            log_data["method"] = record.method
        if hasattr(record, "path"):
            log_data["path"] = record.path
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code

        # Add any other extra attributes
        for key, value in record.__dict__.items():
            if key not in log_data and not key.startswith("_"):
                if key not in [
                    "name",
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "pathname",
                    "filename",
                    "module",
                    "lineno",
                    "funcName",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "processName",
                    "process",
                ]:
                    log_data[key] = value

        try:
            return json.dumps(log_data, default=str)
        except (TypeError, ValueError):
            # Fallback to standard formatting if JSON serialization fails
            return super().format(record)


def get_structured_logger(name: str, **extra_data: Any) -> StructuredLoggerAdapter:
    """
    Get a structured logger adapter with extra data.

    Args:
        name: The logger name
        **extra_data: Additional data to include in all log records

    Returns:
        A StructuredLoggerAdapter instance
    """
    base_logger = logging.getLogger(name)
    return StructuredLoggerAdapter(base_logger, extra_data)


def log_performance(
    operation: str,
    duration_ms: float,
    logger_name: str = "performance",
    **extra_data: Any,
) -> None:
    """
    Log performance metrics.

    Args:
        operation: The operation being measured
        duration_ms: Duration in milliseconds
        logger_name: Name of the logger to use
        **extra_data: Additional data to include
    """
    perf_logger = get_structured_logger(
        logger_name, operation=operation, duration_ms=duration_ms, **extra_data
    )
    perf_logger.info(f"Operation '{operation}' completed in {duration_ms:.2f}ms")


def log_error(
    error: Exception,
    component: str,
    severity: str = "medium",
    logger_name: str = "error",
    **extra_data: Any,
) -> None:
    """
    Log structured error information.

    Args:
        error: The exception that occurred
        component: The component where the error occurred
        severity: Error severity (low, medium, high, critical)
        logger_name: Name of the logger to use
        **extra_data: Additional data to include
    """
    error_logger = get_structured_logger(
        logger_name,
        error_type=type(error).__name__,
        component=component,
        severity=severity,
        error_message=str(error),
        **extra_data,
    )
    error_logger.error(f"Error in {component}: {error}")
