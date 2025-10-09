from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.auth.utils import pwd_context
from backend.models.history import QuestionHistory
from backend.models.topic import Topic
from backend.models.user import User


@pytest.fixture
def admin_user(db_session: Session) -> User:
    user = User(
        username="admin",
        email="admin@example.com",
        password=pwd_context.hash("adminpass"),
        is_staff=True,
        is_superuser=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def regular_user(db_session: Session) -> User:
    user = User(
        username="user",
        email="user@example.com",
        password=pwd_context.hash("userpass"),
        is_staff=False,
        is_superuser=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(client: TestClient, admin_user: User) -> str:
    response = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "adminpass"},
    )
    return response.json()["access_token"]


@pytest.fixture
def user_token(client: TestClient, regular_user: User) -> str:
    response = client.post(
        "/api/auth/login",
        data={"username": "user", "password": "userpass"},
    )
    return response.json()["access_token"]


def test_analytics_summary_empty_data(client: TestClient, admin_token: str) -> None:
    response = client.get(
        "/api/admin/analytics/summary",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_questions"] == 0
    assert data["total_feedback"] == 0
    assert data["active_sessions"] == 0
    assert data["average_feedback_score"] == 0.0


def test_analytics_summary_with_data(
    db_session: Session, client: TestClient, admin_token: str
) -> None:
    topic = Topic(
        name="Test Topic",
        description="Test",
        system_prompt="Test prompt",
    )
    db_session.add(topic)
    db_session.commit()

    history1 = QuestionHistory(
        topic_id=topic.id,
        question="Q1",
        answer="A1",
        session_id="session1",
        feedback_score=1,
    )
    history2 = QuestionHistory(
        topic_id=topic.id,
        question="Q2",
        answer="A2",
        session_id="session2",
        feedback_score=-1,
    )
    history3 = QuestionHistory(
        topic_id=topic.id,
        question="Q3",
        answer="A3",
        session_id="session1",
        feedback_score=0,
    )
    db_session.add_all([history1, history2, history3])
    db_session.commit()

    response = client.get(
        "/api/admin/analytics/summary",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_questions"] == 3
    assert data["total_feedback"] == 2
    assert data["active_sessions"] == 2
    assert data["average_feedback_score"] == pytest.approx(0.0, abs=0.01)


def test_analytics_topics_stats(
    db_session: Session, client: TestClient, admin_token: str
) -> None:
    topic1 = Topic(
        name="Topic 1",
        description="Test",
        system_prompt="Test prompt",
    )
    topic2 = Topic(
        name="Topic 2",
        description="Test",
        system_prompt="Test prompt",
    )
    db_session.add_all([topic1, topic2])
    db_session.commit()

    history1 = QuestionHistory(
        topic_id=topic1.id,
        question="Q1",
        answer="A1",
        session_id="session1",
        feedback_score=1,
    )
    history2 = QuestionHistory(
        topic_id=topic1.id,
        question="Q2",
        answer="A2",
        session_id="session1",
        feedback_score=1,
    )
    db_session.add_all([history1, history2])
    db_session.commit()

    response = client.get(
        "/api/admin/analytics/topics",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    topic1_stats = next((t for t in data if t["topic_id"] == topic1.id), None)
    assert topic1_stats is not None
    assert topic1_stats["topic_name"] == "Topic 1"
    assert topic1_stats["question_count"] == 2
    assert topic1_stats["average_feedback_score"] == pytest.approx(1.0)

    topic2_stats = next((t for t in data if t["topic_id"] == topic2.id), None)
    assert topic2_stats is not None
    assert topic2_stats["question_count"] == 0


def test_analytics_questions_trend_7days(
    db_session: Session, client: TestClient, admin_token: str
) -> None:
    topic = Topic(
        name="Test Topic",
        description="Test",
        system_prompt="Test prompt",
    )
    db_session.add(topic)
    db_session.commit()

    now = datetime.now(UTC)
    history1 = QuestionHistory(
        topic_id=topic.id,
        question="Q1",
        answer="A1",
        session_id="session1",
        created_at=now,
    )
    history2 = QuestionHistory(
        topic_id=topic.id,
        question="Q2",
        answer="A2",
        session_id="session1",
        created_at=now - timedelta(days=1),
    )
    history3 = QuestionHistory(
        topic_id=topic.id,
        question="Q3",
        answer="A3",
        session_id="session1",
        created_at=now - timedelta(days=10),
    )
    db_session.add_all([history1, history2, history3])
    db_session.commit()

    response = client.get(
        "/api/admin/analytics/questions/trend?days=7",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all("date" in item and "question_count" in item for item in data)


def test_analytics_feedback_distribution(
    db_session: Session, client: TestClient, admin_token: str
) -> None:
    topic = Topic(
        name="Test Topic",
        description="Test",
        system_prompt="Test prompt",
    )
    db_session.add(topic)
    db_session.commit()

    history1 = QuestionHistory(
        topic_id=topic.id,
        question="Q1",
        answer="A1",
        session_id="session1",
        feedback_score=1,
    )
    history2 = QuestionHistory(
        topic_id=topic.id,
        question="Q2",
        answer="A2",
        session_id="session1",
        feedback_score=-1,
    )
    history3 = QuestionHistory(
        topic_id=topic.id,
        question="Q3",
        answer="A3",
        session_id="session1",
        feedback_score=0,
    )
    db_session.add_all([history1, history2, history3])
    db_session.commit()

    response = client.get(
        "/api/admin/analytics/feedback/distribution",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["positive"] == 1
    assert data["neutral"] == 1
    assert data["negative"] == 1


def test_feedback_comments_empty(
    client: TestClient,
    admin_token: str,
) -> None:
    response = client.get(
        "/api/admin/analytics/feedback/comments",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json() == []


def test_feedback_comments_with_data(
    db_session: Session,
    client: TestClient,
    admin_token: str,
) -> None:
    topic1 = Topic(
        name="History Topic",
        description="Test",
        system_prompt="Prompt",
    )
    topic2 = Topic(
        name="Science Topic",
        description="Test",
        system_prompt="Prompt",
    )
    db_session.add_all([topic1, topic2])
    db_session.commit()

    older = datetime(2024, 1, 1, 12, 0, tzinfo=UTC)
    newer = datetime(2024, 1, 2, 9, 30, tzinfo=UTC)

    comment1 = QuestionHistory(
        topic_id=topic1.id,
        question="Q1",
        answer="A1",
        session_id="s1",
        feedback_score=1,
        feedback_comment="매우 유용했어요",
        created_at=older,
    )
    comment2 = QuestionHistory(
        topic_id=topic2.id,
        question="Q2",
        answer="A2",
        session_id="s2",
        feedback_score=-1,
        feedback_comment="답변이 부족했습니다",
        created_at=newer,
    )
    no_comment = QuestionHistory(
        topic_id=topic1.id,
        question="Q3",
        answer="A3",
        session_id="s1",
        feedback_score=0,
        feedback_comment=None,
    )
    db_session.add_all([comment1, comment2, no_comment])
    db_session.commit()

    response = client.get(
        "/api/admin/analytics/feedback/comments",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert [item["history_id"] for item in data] == [comment2.id, comment1.id]
    assert data[0]["topic_id"] == topic2.id
    assert data[0]["feedback_score"] == -1
    assert data[0]["feedback_comment"] == "답변이 부족했습니다"
    assert "created_at" in data[0]

    response_filtered = client.get(
        f"/api/admin/analytics/feedback/comments?topic_id={topic1.id}&limit=1",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response_filtered.status_code == 200
    filtered = response_filtered.json()
    assert len(filtered) == 1
    first = filtered[0]
    assert first["history_id"] == comment1.id
    assert first["topic_id"] == topic1.id
    assert first["topic_name"] == "History Topic"
    assert first["feedback_score"] == 1
    assert first["feedback_comment"] == "매우 유용했어요"
    assert "created_at" in first


def test_analytics_require_admin(client: TestClient, user_token: str) -> None:
    response = client.get(
        "/api/admin/analytics/summary",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
