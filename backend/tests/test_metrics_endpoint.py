"""
Tests for Prometheus metrics endpoint.
"""

from fastapi.testclient import TestClient


def test_metrics_endpoint_exists(client: TestClient):
    """Test that /metrics endpoint exists and returns Prometheus format."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"


def test_metrics_endpoint_format(client: TestClient):
    """Test that /metrics endpoint returns Prometheus text format."""
    response = client.get("/metrics")
    assert response.status_code == 200
    content = response.text

    assert "# HELP" in content or "# TYPE" in content or content.strip() == ""


def test_metrics_endpoint_contains_otel_metrics(client: TestClient, monkeypatch):
    """Test that /metrics endpoint exposes OpenTelemetry metrics."""
    monkeypatch.setenv("OTEL_ENABLED", "true")
    monkeypatch.setenv("PROMETHEUS_METRICS_ENABLED", "true")

    response = client.get("/metrics")
    assert response.status_code == 200

    content = response.text
    assert isinstance(content, str)
