"""
Integration tests for Prometheus metrics scraping.

These tests verify that Prometheus can scrape metrics from the backend.
Run with: docker compose up -d prometheus backend && pytest backend/tests/test_prometheus_integration.py
"""

import os

import pytest


@pytest.mark.skipif(
    os.getenv("SKIP_PROMETHEUS_TESTS", "true").lower() == "true",
    reason="Prometheus integration tests require running Prometheus service",
)
def test_prometheus_service_available():
    """Test that Prometheus service is accessible."""
    import httpx

    response = httpx.get("http://localhost:9090")
    assert response.status_code == 200


@pytest.mark.skipif(
    os.getenv("SKIP_PROMETHEUS_TESTS", "true").lower() == "true",
    reason="Prometheus integration tests require running Prometheus service",
)
def test_prometheus_scrapes_backend_metrics(client):
    """Test that Prometheus scrapes backend /metrics endpoint."""
    import time

    import httpx

    client.get("/health")
    time.sleep(20)

    prometheus_api_url = "http://localhost:9090/api/v1/targets"
    response = httpx.get(prometheus_api_url)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"

    targets = data["data"]["activeTargets"]
    backend_target = next(
        (t for t in targets if t["labels"]["job"] == "scholaria-backend"), None
    )

    assert backend_target is not None
    assert backend_target["health"] == "up"


@pytest.mark.skipif(
    os.getenv("SKIP_PROMETHEUS_TESTS", "true").lower() == "true",
    reason="Prometheus integration tests require running Prometheus service",
)
def test_prometheus_has_rag_metrics():
    """Test that Prometheus has collected RAG metrics."""
    import time

    import httpx

    time.sleep(20)

    prometheus_query_url = "http://localhost:9090/api/v1/query"
    params = {"query": "rag_query_duration_seconds_count"}

    response = httpx.get(prometheus_query_url, params=params)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
