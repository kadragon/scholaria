"""
Tests for FastAPI Contexts endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


def test_list_contexts_empty(client):
    """Test listing contexts returns empty list when no contexts exist."""
    response = client.get("/api/contexts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.skip(reason="Django ORM dependency removed")
def test_list_contexts_with_data(client):
    """Test listing contexts returns data from Django database."""
    pass


@pytest.mark.skip(reason="Django ORM dependency removed")
def test_get_context_by_id(client):
    """Test getting a single context by ID."""
    pass


def test_get_context_not_found(client):
    """Test getting non-existent context returns 404."""
    response = client.get("/api/contexts/99999")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
