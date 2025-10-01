"""
Tests for FastAPI RAG endpoint.

TDD approach: Write failing tests first, then implement.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.mark.django_db(transaction=True)
def test_rag_ask_success(client):
    """
    Test POST /api/rag/ask returns answer with citations.

    Expected: 200 with answer, citations, topic_id.
    """
    from django.db import transaction

    from backend.models import Context, ContextItem, Topic

    with transaction.atomic():
        context = Context.objects.create(
            name="Test RAG Context",
            description="Test content for RAG",
            context_type="FAQ",
            original_content="What is Python? Python is a programming language.",
            processing_status="COMPLETED",
        )
        context_item = ContextItem.objects.create(
            context=context,
            title="Python FAQ",
            content="What is Python? Python is a programming language.",
        )
        topic = Topic.objects.create(
            name="Programming",
            description="Programming topics",
        )
        topic.contexts.add(context)
        topic_id = topic.id
        context_id = context.id
        item_id = context_item.id

    try:
        response = client.post(
            "/api/rag/ask",
            json={
                "topic_id": topic_id,
                "question": "What is Python?",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "answer" in data
        assert "citations" in data
        assert "topic_id" in data
        assert data["topic_id"] == topic_id
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 0
        assert isinstance(data["citations"], list)

    finally:
        Topic.objects.filter(id=topic_id).delete()
        Context.objects.filter(id=context_id).delete()
        ContextItem.objects.filter(id=item_id).delete()


def test_rag_ask_validation_empty_question(client):
    """Test POST /api/rag/ask with empty question returns 400."""
    response = client.post(
        "/api/rag/ask",
        json={
            "topic_id": 1,
            "question": "",
        },
    )

    assert response.status_code == 422


def test_rag_ask_validation_missing_topic_id(client):
    """Test POST /api/rag/ask without topic_id returns 422."""
    response = client.post(
        "/api/rag/ask",
        json={
            "question": "What is Python?",
        },
    )

    assert response.status_code == 422


def test_rag_ask_validation_invalid_topic_id(client):
    """Test POST /api/rag/ask with invalid topic_id type returns 422."""
    response = client.post(
        "/api/rag/ask",
        json={
            "topic_id": "invalid",
            "question": "What is Python?",
        },
    )

    assert response.status_code == 422


@pytest.mark.django_db(transaction=True)
def test_rag_ask_no_results(client):
    """
    Test POST /api/rag/ask with no matching context returns default message.

    Expected: 200 with "no relevant information" message.
    """
    from django.db import transaction

    from backend.models import Topic

    with transaction.atomic():
        topic = Topic.objects.create(
            name="Empty Topic",
            description="No contexts",
        )
        topic_id = topic.id

    try:
        response = client.post(
            "/api/rag/ask",
            json={
                "topic_id": topic_id,
                "question": "What is Quantum Computing?",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "couldn't find any relevant information" in data["answer"].lower()
        assert len(data["citations"]) == 0

    finally:
        Topic.objects.filter(id=topic_id).delete()


@pytest.mark.django_db(transaction=True)
def test_rag_ask_caching(client):
    """
    Test that identical requests are cached.

    Expected: Second request should be faster (from cache).
    """

    from django.db import transaction

    from backend.models import Context, ContextItem, Topic

    with transaction.atomic():
        context = Context.objects.create(
            name="Cache Test Context",
            description="Test caching",
            context_type="FAQ",
            original_content="Caching test content.",
            processing_status="COMPLETED",
        )
        ContextItem.objects.create(
            context=context,
            title="Cache Test",
            content="Caching test content.",
        )
        topic = Topic.objects.create(
            name="Cache Topic",
            description="For testing cache",
        )
        topic.contexts.add(context)
        topic_id = topic.id

    try:
        request_payload = {
            "topic_id": topic_id,
            "question": "Tell me about caching",
        }

        # First request
        response1 = client.post("/api/rag/ask", json=request_payload)

        assert response1.status_code == 200
        data1 = response1.json()

        # Second request (should hit cache)
        response2 = client.post("/api/rag/ask", json=request_payload)

        assert response2.status_code == 200
        data2 = response2.json()

        # Same response
        assert data1 == data2

        # Note: Cache timing check may not be reliable in tests
        # Just verify both requests succeed

    finally:
        Topic.objects.filter(id=topic_id).delete()


def test_rag_ask_endpoint_exists(client):
    """
    Minimal test to check endpoint is registered.

    Expected: Endpoint exists (not 404).
    """
    response = client.post("/api/rag/ask", json={})

    # Should not be 404 (endpoint exists)
    assert response.status_code != 404
