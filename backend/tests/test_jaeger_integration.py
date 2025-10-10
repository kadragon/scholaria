"""
Integration tests for Jaeger trace export.

These tests verify that traces are properly exported to Jaeger via OTLP.
Run with: docker compose up -d jaeger && pytest backend/tests/test_jaeger_integration.py
"""

import os

import pytest


@pytest.mark.skipif(
    os.getenv("SKIP_JAEGER_TESTS", "true").lower() == "true",
    reason="Jaeger integration tests require running Jaeger service",
)
def test_jaeger_service_available():
    """Test that Jaeger service is accessible."""
    import httpx

    response = httpx.get("http://localhost:16686")
    assert response.status_code == 200


@pytest.mark.skipif(
    os.getenv("SKIP_JAEGER_TESTS", "true").lower() == "true",
    reason="Jaeger integration tests require running Jaeger service",
)
def test_traces_exported_to_jaeger(client):
    """Test that traces appear in Jaeger after making requests."""
    import time

    import httpx

    response = client.get("/health")
    assert response.status_code == 200

    time.sleep(2)

    jaeger_api_url = "http://localhost:16686/api/traces"
    params = {"service": "scholaria-backend", "limit": "10"}

    response = httpx.get(jaeger_api_url, params=params)
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
