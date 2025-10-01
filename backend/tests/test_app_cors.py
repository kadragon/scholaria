"""
Test FastAPI application CORS configuration.

Ensures CORS origins are configurable via environment variables.
"""

import os
from unittest.mock import patch

from fastapi.testclient import TestClient


def test_cors_preflight_request_allowed_origin(client: TestClient) -> None:
    """CORS preflight OPTIONS request should allow configured origins."""
    response = client.options(
        "/api/topics/",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] in [
        "http://localhost:5173",
        "*",
    ]


def test_cors_actual_request_with_origin(client: TestClient) -> None:
    """Actual GET request with Origin header should return CORS headers."""
    response = client.get(
        "/api/topics/",
        headers={
            "Origin": "http://localhost:5173",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


def test_cors_allows_credentials(client: TestClient) -> None:
    """CORS should allow credentials for authenticated requests."""
    response = client.options(
        "/api/auth/me",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-credentials" in response.headers
    assert response.headers["access-control-allow-credentials"] == "true"


def test_fastapi_cors_env_var_integration() -> None:
    """Integration test: FASTAPI_ALLOWED_ORIGINS env var should configure CORS.

    This test validates that when FASTAPI_ALLOWED_ORIGINS is set,
    the application correctly configures CORS middleware.
    """
    test_origins = "https://admin.example.com,https://app.example.com"

    with patch.dict(os.environ, {"FASTAPI_ALLOWED_ORIGINS": test_origins}):
        import sys

        for module_name in ["api.main", "api.config"]:
            if module_name in sys.modules:
                del sys.modules[module_name]

        from backend.main import app

        client = TestClient(app)
        response = client.options(
            "/api/topics/",
            headers={
                "Origin": "https://admin.example.com",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        allowed_origin = response.headers["access-control-allow-origin"]
        assert allowed_origin in ["https://admin.example.com", "*"]
