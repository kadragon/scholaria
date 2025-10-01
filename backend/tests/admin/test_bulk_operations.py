from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models.context import Context, ContextItem
from backend.models.topic import Topic


class TestBulkAssignContextToTopic:
    def test_bulk_assign_contexts_to_topic_success(
        self, client: TestClient, db_session: Session, admin_headers: dict[str, str]
    ) -> None:
        topic = Topic(name="Test Topic", description="Test Description")
        db_session.add(topic)
        db_session.flush()

        contexts = [
            Context(
                name=f"Context {i}",
                description=f"Description {i}",
                context_type="MARKDOWN",
                original_content=f"Content {i}",
                chunk_count=1,
                processing_status="COMPLETED",
            )
            for i in range(5)
        ]
        db_session.add_all(contexts)
        db_session.commit()

        context_ids = [c.id for c in contexts]

        response = client.post(
            "/api/admin/bulk/assign-context-to-topic",
            json={"context_ids": context_ids, "topic_id": topic.id},
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["assigned_count"] == 5
        assert data["topic_id"] == topic.id

        db_session.refresh(topic)
        assert len(topic.contexts) == 5

    def test_bulk_assign_empty_context_ids(
        self, client: TestClient, db_session: Session, admin_headers: dict[str, str]
    ) -> None:
        topic = Topic(name="Test Topic", description="Test Description")
        db_session.add(topic)
        db_session.commit()

        response = client.post(
            "/api/admin/bulk/assign-context-to-topic",
            json={"context_ids": [], "topic_id": topic.id},
            headers=admin_headers,
        )

        assert response.status_code == 422

    def test_bulk_assign_nonexistent_topic(
        self, client: TestClient, db_session: Session, admin_headers: dict[str, str]
    ) -> None:
        contexts = [
            Context(
                name=f"Context {i}",
                description=f"Description {i}",
                context_type="MARKDOWN",
                original_content=f"Content {i}",
                chunk_count=1,
                processing_status="COMPLETED",
            )
            for i in range(3)
        ]
        db_session.add_all(contexts)
        db_session.commit()

        context_ids = [c.id for c in contexts]

        response = client.post(
            "/api/admin/bulk/assign-context-to-topic",
            json={"context_ids": context_ids, "topic_id": 99999},
            headers=admin_headers,
        )

        assert response.status_code == 404

    def test_bulk_assign_requires_admin(
        self, client: TestClient, db_session: Session
    ) -> None:
        from backend.auth.utils import pwd_context
        from backend.models.user import User

        password = "UserPass123!"
        regular_user = User(
            username="regularuser",
            email="user@test.com",
            password=pwd_context.hash(password),
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )
        db_session.add(regular_user)
        db_session.commit()
        db_session.refresh(regular_user)

        login_response = client.post(
            "/api/auth/login",
            data={"username": "regularuser", "password": password},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/admin/bulk/assign-context-to-topic",
            json={"context_ids": [1], "topic_id": 1},
            headers=headers,
        )

        assert response.status_code == 403


class TestBulkRegenerateEmbeddings:
    def test_bulk_regenerate_embeddings_success(
        self, client: TestClient, db_session: Session, admin_headers: dict[str, str]
    ) -> None:
        contexts = [
            Context(
                name=f"Context {i}",
                description=f"Description {i}",
                context_type="MARKDOWN",
                original_content=f"Content {i}",
                chunk_count=1,
                processing_status="COMPLETED",
            )
            for i in range(3)
        ]
        db_session.add_all(contexts)
        db_session.commit()

        items = []
        for ctx in contexts:
            item = ContextItem(
                title=f"Chunk for {ctx.name}",
                content="sample chunk",
                context_id=ctx.id,
                item_metadata="{}",
            )
            db_session.add(item)
            items.append(item)
        db_session.commit()

        context_ids = [c.id for c in contexts]

        with patch(
            "backend.tasks.embeddings.regenerate_embedding_task.delay"
        ) as mock_delay:
            mock_delay.return_value.id = "task-123"
            response = client.post(
                "/api/admin/bulk/regenerate-embeddings",
                json={"context_ids": context_ids},
                headers=admin_headers,
            )

        assert response.status_code == 202
        data = response.json()
        assert data["queued_count"] == len(items)
        assert "task_ids" in data
        assert len(data["task_ids"]) == len(items)
        assert mock_delay.call_count == len(items)

    def test_bulk_regenerate_empty_ids(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        response = client.post(
            "/api/admin/bulk/regenerate-embeddings",
            json={"context_ids": []},
            headers=admin_headers,
        )

        assert response.status_code == 422

    def test_bulk_regenerate_requires_admin(
        self, client: TestClient, db_session: Session
    ) -> None:
        from backend.auth.utils import pwd_context
        from backend.models.user import User

        password = "UserPass123!"
        regular_user = User(
            username="regularuser",
            email="user@test.com",
            password=pwd_context.hash(password),
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )
        db_session.add(regular_user)
        db_session.commit()
        db_session.refresh(regular_user)

        login_response = client.post(
            "/api/auth/login",
            data={"username": "regularuser", "password": password},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/admin/bulk/regenerate-embeddings",
            json={"context_ids": [1]},
            headers=headers,
        )

        assert response.status_code == 403


class TestBulkUpdateSystemPrompt:
    def test_bulk_update_system_prompt_success(
        self, client: TestClient, db_session: Session, admin_headers: dict[str, str]
    ) -> None:
        topics = [
            Topic(
                name=f"Topic {i}",
                description=f"Desc {i}",
                system_prompt=f"Old prompt {i}",
            )
            for i in range(3)
        ]
        db_session.add_all(topics)
        db_session.commit()

        topic_ids = [t.id for t in topics]
        new_prompt = "Updated system prompt for all"

        response = client.post(
            "/api/admin/bulk/update-system-prompt",
            json={"topic_ids": topic_ids, "system_prompt": new_prompt},
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["updated_count"] == 3

        for topic in topics:
            db_session.refresh(topic)
            assert topic.system_prompt == new_prompt

    def test_bulk_update_empty_topic_ids(
        self, client: TestClient, admin_headers: dict[str, str]
    ) -> None:
        response = client.post(
            "/api/admin/bulk/update-system-prompt",
            json={"topic_ids": [], "system_prompt": "New prompt"},
            headers=admin_headers,
        )

        assert response.status_code == 422

    def test_bulk_update_requires_admin(
        self, client: TestClient, db_session: Session
    ) -> None:
        from backend.auth.utils import pwd_context
        from backend.models.user import User

        password = "UserPass123!"
        regular_user = User(
            username="regularuser",
            email="user@test.com",
            password=pwd_context.hash(password),
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )
        db_session.add(regular_user)
        db_session.commit()
        db_session.refresh(regular_user)

        login_response = client.post(
            "/api/auth/login",
            data={"username": "regularuser", "password": password},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/admin/bulk/update-system-prompt",
            json={"topic_ids": [1], "system_prompt": "New prompt"},
            headers=headers,
        )

        assert response.status_code == 403
