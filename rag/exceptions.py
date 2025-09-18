"""Custom exception handlers for the RAG API."""

import logging
from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(
    exc: Exception, context: dict[str, Any]
) -> Response | None:
    """Custom exception handler that provides user-friendly error messages."""

    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # Log the error with full context
        view = context.get("view")
        request = context.get("request")

        logger.error(
            f"API Error in {view.__class__.__name__ if view else 'Unknown'}: {str(exc)}",
            extra={
                "view_name": view.__class__.__name__ if view else None,
                "method": request.method if request else None,
                "path": request.get_full_path() if request else None,
                "user": getattr(request, "user", None),
            },
            exc_info=True,
        )

        # Customize the error response
        custom_response_data = {
            "error": True,
            "message": "An error occurred while processing your request.",
            "details": response.data if hasattr(response, "data") else str(exc),
            "status_code": response.status_code,
        }

        # Add specific error messages for common scenarios
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            custom_response_data["message"] = "Invalid request data provided."
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            custom_response_data["message"] = "The requested resource was not found."
        elif response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            custom_response_data["message"] = (
                "HTTP method not allowed for this endpoint."
            )
        elif response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            custom_response_data["message"] = (
                "Too many requests. Please try again later."
            )
        elif response.status_code >= 500:
            custom_response_data["message"] = (
                "Internal server error. Please try again later."
            )
            # Don't expose internal error details in production
            custom_response_data["details"] = "Contact support if the problem persists."

        response.data = custom_response_data

    return response
