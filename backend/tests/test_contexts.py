"""
Tests for FastAPI Contexts endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.models.context import Context


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


def test_list_contexts_empty(client):
    """Test listing contexts returns empty list when no contexts exist."""
    response = client.get("/api/contexts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_contexts_with_data(client, db_session):
    """Test listing contexts returns persisted contexts."""
    contexts = [
        Context(
            name="Context A",
            description="Description A",
            context_type="MARKDOWN",
            original_content="# A",
            chunk_count=1,
            processing_status="COMPLETED",
        ),
        Context(
            name="Context B",
            description="Description B",
            context_type="FAQ",
            original_content="Q: B?",
            chunk_count=0,
            processing_status="PENDING",
        ),
    ]
    db_session.add_all(contexts)
    db_session.commit()

    response = client.get("/api/contexts")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    names = {item["name"] for item in payload}
    assert {"Context A", "Context B"}.issubset(names)


def test_get_context_by_id(client, db_session):
    """Test getting a single context by ID."""
    context = Context(
        name="Single Context",
        description="Single description",
        context_type="MARKDOWN",
        original_content="# Single",
        chunk_count=2,
        processing_status="COMPLETED",
    )
    db_session.add(context)
    db_session.commit()
    db_session.refresh(context)

    response = client.get(f"/api/contexts/{context.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == context.id
    assert data["name"] == "Single Context"
    assert data["context_type"] == "MARKDOWN"


def test_get_context_not_found(client):
    """Test getting non-existent context returns 404."""
    response = client.get("/api/contexts/99999")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
