"""Tests for feedback system (like/dislike on Q&A history)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models.history import QuestionHistory
from backend.models.topic import Topic


@pytest.fixture
def sample_topic(db_session: Session) -> Topic:
    """Persist a sample topic for feedback tests."""
    topic = Topic(
        name="Test Topic",
        description="Test description",
        system_prompt="Test prompt",
    )
    db_session.add(topic)
    db_session.commit()
    db_session.refresh(topic)
    return topic


@pytest.fixture
def sample_history(db_session: Session, sample_topic: Topic) -> QuestionHistory:
    """Create a sample question history record."""
    history = QuestionHistory(
        topic_id=sample_topic.id,
        question="Test question?",
        answer="Test answer.",
        session_id="test-session-123",
        feedback_score=0,
    )
    db_session.add(history)
    db_session.commit()
    db_session.refresh(history)
    return history


def test_patch_feedback_like(
    client: TestClient, sample_history: QuestionHistory, admin_headers: dict[str, str]
) -> None:
    """Test setting feedback to like (1)."""
    response = client.patch(
        f"/api/history/{sample_history.id}/feedback",
        json={"feedback_score": 1},
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["feedback_score"] == 1
    assert data["id"] == sample_history.id
    assert data["feedback_comment"] is None


def test_patch_feedback_dislike(
    client: TestClient, sample_history: QuestionHistory, admin_headers: dict[str, str]
) -> None:
    """Test setting feedback to dislike (-1)."""
    response = client.patch(
        f"/api/history/{sample_history.id}/feedback",
        json={"feedback_score": -1},
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["feedback_score"] == -1
    assert data["feedback_comment"] is None


def test_patch_feedback_neutral(
    client: TestClient, sample_history: QuestionHistory, admin_headers: dict[str, str]
) -> None:
    """Test setting feedback to neutral (0)."""
    response = client.patch(
        f"/api/history/{sample_history.id}/feedback",
        json={"feedback_score": 0},
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["feedback_score"] == 0
    assert data["feedback_comment"] is None


def test_patch_feedback_invalid_score(
    client: TestClient, sample_history: QuestionHistory, admin_headers: dict[str, str]
) -> None:
    """Test rejection of invalid feedback score (not -1/0/1)."""
    response = client.patch(
        f"/api/history/{sample_history.id}/feedback",
        json={"feedback_score": 5},
        headers=admin_headers,
    )
    assert response.status_code == 422


def test_patch_feedback_not_found(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    """Test 404 when history record doesn't exist."""
    response = client.patch(
        "/api/history/99999/feedback",
        json={"feedback_score": 1},
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_patch_feedback_with_comment(
    client: TestClient,
    sample_history: QuestionHistory,
    admin_headers: dict[str, str],
    db_session: Session,
) -> None:
    """Test setting feedback with an explanatory comment."""
    payload = {
        "feedback_score": -1,
        "feedback_comment": "The answer was irrelevant to my question.",
    }
    response = client.patch(
        f"/api/history/{sample_history.id}/feedback",
        json=payload,
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["feedback_score"] == -1
    assert data["feedback_comment"] == payload["feedback_comment"]

    db_session.expire_all()
    saved = db_session.get(QuestionHistory, sample_history.id)
    assert saved is not None
    assert saved.feedback_comment == payload["feedback_comment"]


def test_patch_feedback_clear_comment(
    client: TestClient,
    sample_history: QuestionHistory,
    admin_headers: dict[str, str],
    db_session: Session,
) -> None:
    """Test clearing an existing feedback comment."""
    # Seed comment
    sample_history.feedback_comment = "Initial comment"
    db_session.commit()

    response = client.patch(
        f"/api/history/{sample_history.id}/feedback",
        json={"feedback_score": 1, "feedback_comment": None},
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["feedback_score"] == 1
    assert data["feedback_comment"] is None

    db_session.expire_all()
    refreshed = db_session.get(QuestionHistory, sample_history.id)
    assert refreshed is not None
    assert refreshed.feedback_comment is None


def test_get_history_includes_feedback_score(
    client: TestClient,
    db_session: Session,
    sample_topic: Topic,
    admin_headers: dict[str, str],
) -> None:
    """Test that GET /history includes feedback_score field."""
    # Create history with feedback
    history = QuestionHistory(
        topic_id=sample_topic.id,
        question="Test?",
        answer="Answer.",
        session_id="sess-1",
        feedback_score=1,
    )
    db_session.add(history)
    db_session.commit()

    response = client.get(
        "/api/history",
        params={"topic_id": sample_topic.id},
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "feedback_score" in data[0]
    assert data[0]["feedback_score"] == 1
    assert "feedback_comment" in data[0]
    assert data[0]["feedback_comment"] is None
