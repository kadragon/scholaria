"""Tests for session history endpoints."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from backend.main import app
from backend.models.history import QuestionHistory
from backend.models.topic import Topic

client = TestClient(app)


class TestSessionHistoryEndpoint:
    """Test session-based conversation history retrieval."""

    def test_create_history_record(self, db_session) -> None:
        """POST /history should persist question/answer pair."""
        topic = Topic(
            name="Sample Topic",
            slug="sample-topic",
            description="Desc",
            system_prompt="Prompt",
        )
        db_session.add(topic)
        db_session.commit()

        payload = {
            "topic_id": topic.id,
            "question": "What is the schedule?",
            "answer": "Classes start at 9 AM.",
            "session_id": "sess-123",
        }

        response = client.post("/api/history", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["question"] == payload["question"]
        assert data["answer"] == payload["answer"]
        assert data["session_id"] == payload["session_id"]
        topic_value = data.get("topic") or data.get("topic_id")
        assert topic_value == topic.id
        assert data["feedback_score"] == 0
        assert data["feedback_comment"] is None

    def test_create_history_requires_valid_topic(self, db_session) -> None:
        """POST /history should return 404 when topic does not exist."""
        payload = {
            "topic_id": 999,
            "question": "Missing topic?",
            "answer": "No topic.",
            "session_id": "sess-404",
        }

        response = client.post("/api/history", json=payload)
        assert response.status_code == 404
        assert response.json()["detail"] == "Topic not found"

    def test_get_session_history_empty(self, db_session) -> None:
        """Should return empty list for non-existent session."""
        response = client.get("/api/history/session/nonexistent-session")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_session_history_with_data(self, db_session) -> None:
        """Should return conversation history ordered by created_at."""
        session_id = "test-session-123"

        history1 = QuestionHistory(
            topic_id=1,
            question="First question?",
            answer="First answer",
            session_id=session_id,
            created_at=datetime(2024, 1, 1, 10, 0, tzinfo=UTC),
        )
        history2 = QuestionHistory(
            topic_id=1,
            question="Second question?",
            answer="Second answer",
            session_id=session_id,
            created_at=datetime(2024, 1, 1, 10, 5, tzinfo=UTC),
        )
        history3 = QuestionHistory(
            topic_id=1,
            question="Other session question?",
            answer="Other answer",
            session_id="other-session",
            created_at=datetime(2024, 1, 1, 10, 3, tzinfo=UTC),
        )

        db_session.add_all([history1, history2, history3])
        db_session.commit()

        response = client.get(f"/api/history/session/{session_id}")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 2
        assert data[0]["question"] == "First question?"
        assert data[1]["question"] == "Second question?"
        assert data[0]["session_id"] == session_id
        assert data[1]["session_id"] == session_id

    def test_conversation_message_schema(self) -> None:
        """ConversationMessage schema should serialize properly."""
        from backend.schemas.history import ConversationMessage

        msg = ConversationMessage(
            role="user",
            content="Test question?",
            timestamp=datetime(2024, 1, 1, 12, 0, tzinfo=UTC),
        )

        assert msg.role == "user"
        assert msg.content == "Test question?"
        assert "2024-01-01" in msg.model_dump_json()
