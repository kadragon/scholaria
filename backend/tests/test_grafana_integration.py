"""
Integration tests for Grafana dashboard provisioning.

These tests verify that Grafana datasources and dashboards are properly configured.
Run with: docker compose up -d grafana && pytest backend/tests/test_grafana_integration.py
"""

import os

import pytest


@pytest.mark.skipif(
    os.getenv("SKIP_GRAFANA_TESTS", "true").lower() == "true",
    reason="Grafana integration tests require running Grafana service",
)
def test_grafana_service_available():
    """Test that Grafana service is accessible."""
    import httpx

    response = httpx.get("http://localhost:3001", follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.skipif(
    os.getenv("SKIP_GRAFANA_TESTS", "true").lower() == "true",
    reason="Grafana integration tests require running Grafana service",
)
def test_grafana_datasources_provisioned():
    """Test that Grafana datasources are provisioned."""
    import time

    import httpx

    time.sleep(10)

    auth = ("admin", "admin")
    response = httpx.get("http://localhost:3001/api/datasources", auth=auth)
    assert response.status_code == 200

    datasources = response.json()
    datasource_names = [ds["name"] for ds in datasources]

    assert "Prometheus" in datasource_names
    assert "Jaeger" in datasource_names


@pytest.mark.skipif(
    os.getenv("SKIP_GRAFANA_TESTS", "true").lower() == "true",
    reason="Grafana integration tests require running Grafana service",
)
def test_grafana_dashboard_exists():
    """Test that RAG dashboard is provisioned."""
    import time

    import httpx

    time.sleep(10)

    auth = ("admin", "admin")
    response = httpx.get("http://localhost:3001/api/search?type=dash-db", auth=auth)
    assert response.status_code == 200

    dashboards = response.json()
    dashboard_titles = [db["title"] for db in dashboards]

    assert "Scholaria RAG Pipeline" in dashboard_titles
