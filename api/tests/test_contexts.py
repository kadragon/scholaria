"""
Tests for FastAPI Contexts endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


def test_list_contexts_empty(client):
    """Test listing contexts returns empty list when no contexts exist."""
    response = client.get("/api/contexts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.django_db(transaction=True)
def test_list_contexts_with_data(client):
    """Test listing contexts returns data from Django database."""
    from django.db import transaction

    from rag.models import Context

    # Create test data with explicit transaction
    with transaction.atomic():
        context = Context.objects.create(
            name="Test Context",
            description="Test Description",
            context_type="PDF",
        )
        context_id = context.id

    try:
        response = client.get("/api/contexts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

        # Find our test context
        test_context = next((c for c in data if c["id"] == context_id), None)
        assert test_context is not None
        assert test_context["name"] == "Test Context"
        assert test_context["description"] == "Test Description"
        assert test_context["context_type"] == "PDF"
        assert test_context["processing_status"] == "PENDING"
    finally:
        # Cleanup
        Context.objects.filter(id=context_id).delete()


@pytest.mark.django_db(transaction=True)
def test_get_context_by_id(client):
    """Test getting a single context by ID."""
    from django.db import transaction

    from rag.models import Context

    # Create test data
    with transaction.atomic():
        context = Context.objects.create(
            name="Single Context",
            description="Single Description",
            context_type="FAQ",
        )
        context_id = context.id

    try:
        response = client.get(f"/api/contexts/{context_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == context_id
        assert data["name"] == "Single Context"
        assert data["context_type"] == "FAQ"
    finally:
        # Cleanup
        Context.objects.filter(id=context_id).delete()


def test_get_context_not_found(client):
    """Test getting a non-existent context returns 404."""
    response = client.get("/api/contexts/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Context not found"
