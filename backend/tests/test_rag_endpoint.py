"""
Tests for FastAPI RAG endpoint.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


@pytest.fixture
def mock_rag_service():
    """Mock AsyncRAGService for testing."""
    with patch("backend.routers.rag.AsyncRAGService") as mock_service_class:
        mock_service = AsyncMock()
        mock_service_class.return_value = mock_service
        yield mock_service


@pytest.fixture
def mock_redis():
    """Mock Redis dependency."""
    with patch("backend.routers.rag.get_redis") as mock:
        mock_redis_client = AsyncMock()
        mock.return_value = mock_redis_client
        yield mock_redis_client


@pytest.fixture(autouse=True)
def auto_set_openai_key(monkeypatch):
    """Automatically set OPENAI_API_KEY for all tests in this module."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")


def test_ask_question_success(mock_rag_service, mock_redis):
    """Test successful question answering."""
    mock_rag_service.query.return_value = {
        "answer": "This is a test answer.",
        "sources": [
            {
                "title": "Test Source",
                "content": "Test content for the source.",
                "score": 0.95,
                "context_type": "MARKDOWN",
                "context_item_id": 1,
            }
        ],
    }

    response = client.post(
        "/api/rag/ask",
        json={
            "topic_id": 1,
            "question": "What is the test question?",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["answer"] == "This is a test answer."
    assert data["topic_id"] == 1
    assert len(data["citations"]) == 1
    assert data["citations"][0]["title"] == "Test Source"
    assert data["citations"][0]["score"] == 0.95


def test_ask_question_empty_question_fails():
    """Test that empty question returns 422 validation error."""
    response = client.post(
        "/api/rag/ask",
        json={
            "topic_id": 1,
            "question": "",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_ask_question_invalid_topic_id_fails():
    """Test that invalid topic_id returns 422 validation error."""
    response = client.post(
        "/api/rag/ask",
        json={
            "topic_id": 0,
            "question": "Valid question",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_ask_question_service_value_error(mock_rag_service, mock_redis):
    """Test that ValueError from service returns 400."""
    mock_rag_service.query.side_effect = ValueError("Invalid parameters")

    response = client.post(
        "/api/rag/ask",
        json={
            "topic_id": 1,
            "question": "Test question",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid request parameters" in response.json()["detail"]


def test_ask_question_service_connection_error(mock_rag_service, mock_redis):
    """Test that ConnectionError from service returns 503."""
    mock_rag_service.query.side_effect = ConnectionError("Service unavailable")

    response = client.post(
        "/api/rag/ask",
        json={
            "topic_id": 1,
            "question": "Test question",
        },
    )

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "Unable to connect" in response.json()["detail"]


def test_ask_question_service_generic_error(mock_rag_service, mock_redis):
    """Test that generic Exception from service returns 500."""
    mock_rag_service.query.side_effect = Exception("Unexpected error")

    response = client.post(
        "/api/rag/ask",
        json={
            "topic_id": 1,
            "question": "Test question",
        },
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "error occurred" in response.json()["detail"]
