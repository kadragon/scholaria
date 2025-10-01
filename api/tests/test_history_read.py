"""Tests for FastAPI question history read endpoint."""

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.mark.django_db(transaction=True)
def test_history_list_by_topic_and_session(client: TestClient) -> None:
    """FastAPI should return history entries filtered by topic and session."""
    from django.db import transaction as django_txn

    from api.models import QuestionHistory, Topic

    with django_txn.atomic():
        topic = Topic.objects.create(name="History Topic", description="Desc")
        older = QuestionHistory.objects.create(
            topic=topic,
            question="Old question?",
            answer="Old answer.",
            session_id="session-1",
        )
        newer = QuestionHistory.objects.create(
            topic=topic,
            question="New question?",
            answer="New answer.",
            session_id="session-1",
        )
        other_session = QuestionHistory.objects.create(
            topic=topic,
            question="Other session question?",
            answer="Other answer.",
            session_id="session-2",
        )

    response = client.get(
        "/api/history",
        params={"topic_id": topic.id, "session_id": "session-1"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    # Should only include session-1 entries ordered newest first
    assert [item["id"] for item in payload] == [newer.id, older.id]
    for item in payload:
        assert item["topic_id"] == topic.id
        assert item["session_id"] == "session-1"
    returned_ids = {item["id"] for item in payload}
    assert other_session.id not in returned_ids


def test_history_requires_topic_id(client: TestClient) -> None:
    """topic_id is required and missing values raise validation error."""
    response = client.get("/api/history")
    assert response.status_code == 422
