"""Tests for Context-Topic N:N relationship management in admin API."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models.context import Context
from backend.models.topic import Topic


@pytest.mark.usefixtures("admin_headers")
class TestContextTopicRelationships:
    def test_update_context_with_topic_ids(
        self, client: TestClient, admin_headers: dict[str, str], db_session: Session
    ) -> None:
        topic1 = Topic(name="Topic 1", description="First topic", system_prompt="P1")
        topic2 = Topic(name="Topic 2", description="Second topic", system_prompt="P2")
        db_session.add_all([topic1, topic2])
        db_session.commit()

        context = Context(
            name="Test Context",
            description="Test",
            context_type="MARKDOWN",
        )
        db_session.add(context)
        db_session.commit()

        response = client.put(
            f"/api/admin/contexts/{context.id}",
            json={"topic_ids": [topic1.id, topic2.id]},
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["topics_count"] == 2

        db_session.refresh(context)
        assert len(context.topics) == 2
        assert {t.id for t in context.topics} == {topic1.id, topic2.id}

    def test_update_context_remove_topics(
        self, client: TestClient, admin_headers: dict[str, str], db_session: Session
    ) -> None:
        topic = Topic(name="Topic 1", description="First topic", system_prompt="P1")
        db_session.add(topic)
        db_session.commit()

        context = Context(
            name="Test Context",
            description="Test",
            context_type="MARKDOWN",
        )
        context.topics = [topic]
        db_session.add(context)
        db_session.commit()

        response = client.put(
            f"/api/admin/contexts/{context.id}",
            json={"topic_ids": []},
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["topics_count"] == 0

        db_session.refresh(context)
        assert len(context.topics) == 0

    def test_list_contexts_includes_topics_count(
        self, client: TestClient, admin_headers: dict[str, str], db_session: Session
    ) -> None:
        topic = Topic(name="Topic 1", description="First topic", system_prompt="P1")
        db_session.add(topic)
        db_session.commit()

        context = Context(
            name="Test Context",
            description="Test",
            context_type="MARKDOWN",
        )
        context.topics = [topic]
        db_session.add(context)
        db_session.commit()

        response = client.get(
            "/api/admin/contexts",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["data"][0]["topics_count"] == 1

    def test_get_context_includes_topics_count(
        self, client: TestClient, admin_headers: dict[str, str], db_session: Session
    ) -> None:
        topic = Topic(name="Topic 1", description="First topic", system_prompt="P1")
        db_session.add(topic)
        db_session.commit()

        context = Context(
            name="Test Context",
            description="Test",
            context_type="MARKDOWN",
        )
        context.topics = [topic]
        db_session.add(context)
        db_session.commit()

        response = client.get(
            f"/api/admin/contexts/{context.id}",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["topics_count"] == 1


@pytest.mark.usefixtures("admin_headers")
class TestTopicContextRelationships:
    def test_get_topic_contexts_count(
        self, client: TestClient, admin_headers: dict[str, str], db_session: Session
    ) -> None:
        context1 = Context(
            name="Context 1", description="First", context_type="MARKDOWN"
        )
        context2 = Context(
            name="Context 2", description="Second", context_type="MARKDOWN"
        )
        db_session.add_all([context1, context2])
        db_session.commit()

        topic = Topic(name="Test Topic", description="Test", system_prompt="Prompt")
        topic.contexts = [context1, context2]
        db_session.add(topic)
        db_session.commit()

        response = client.get(
            f"/api/admin/topics/{topic.id}",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["contexts_count"] == 2
