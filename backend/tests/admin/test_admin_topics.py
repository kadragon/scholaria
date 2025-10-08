"""Tests for Topics Admin API."""

from datetime import datetime

from fastapi.testclient import TestClient

from backend.main import app
from backend.models.context import Context as SQLContext
from backend.models.topic import Topic as SQLTopic

client = TestClient(app)


class TestTopicsAdminList:
    """Test Topics Admin list endpoint."""

    def test_list_topics_requires_admin(self):
        """Test that listing topics requires admin authentication."""
        response = client.get("/api/admin/topics")
        assert response.status_code == 401

    def test_list_topics_empty(self, admin_headers, db_session):
        """Test listing topics when database is empty."""
        response = client.get("/api/admin/topics", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert data["data"] == []
        assert data["total"] == 0

    def test_list_topics_with_data(self, admin_headers, db_session):
        """Test listing topics with existing data."""
        # Create test topics
        topic1 = SQLTopic(
            name="Topic 1",
            description="Description 1",
            system_prompt="Prompt 1",
        )
        topic2 = SQLTopic(
            name="Topic 2",
            description="Description 2",
            system_prompt="Prompt 2",
        )
        db_session.add_all([topic1, topic2])
        db_session.commit()

        response = client.get("/api/admin/topics", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["total"] == 2
        assert data["data"][0]["name"] == "Topic 1"
        assert data["data"][0]["contexts_count"] == 0

    def test_list_topics_with_filter(self, admin_headers, db_session):
        """Test filtering topics by name."""
        topic1 = SQLTopic(
            name="Python Tutorial", description="Desc", system_prompt="Prompt"
        )
        topic2 = SQLTopic(name="Java Guide", description="Desc", system_prompt="Prompt")
        db_session.add_all([topic1, topic2])
        db_session.commit()

        response = client.get(
            "/api/admin/topics",
            params={"filter": '{"name": "Python"}'},
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Python Tutorial"

    def test_list_topics_with_sort(self, admin_headers, db_session):
        """Test sorting topics."""
        topic1 = SQLTopic(name="B Topic", description="Desc", system_prompt="Prompt")
        topic2 = SQLTopic(name="A Topic", description="Desc", system_prompt="Prompt")
        db_session.add_all([topic1, topic2])
        db_session.commit()

        response = client.get(
            "/api/admin/topics",
            params={"sort": "name_asc"},
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"][0]["name"] == "A Topic"
        assert data["data"][1]["name"] == "B Topic"

    def test_list_topics_with_pagination(self, admin_headers, db_session):
        """Test pagination."""
        for i in range(5):
            topic = SQLTopic(
                name=f"Topic {i}", description="Desc", system_prompt="Prompt"
            )
            db_session.add(topic)
        db_session.commit()

        response = client.get(
            "/api/admin/topics",
            params={"skip": 2, "limit": 2},
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["total"] == 5


class TestTopicsAdminCRUD:
    """Test Topics Admin CRUD operations."""

    def test_get_topic(self, admin_headers, db_session):
        """Test getting a single topic."""
        topic = SQLTopic(
            name="Test Topic",
            description="Test Description",
            system_prompt="Test Prompt",
        )
        db_session.add(topic)
        db_session.commit()

        response = client.get(f"/api/admin/topics/{topic.id}", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Topic"
        assert data["contexts_count"] == 0

    def test_get_topic_not_found(self, admin_headers):
        """Test getting non-existent topic."""
        response = client.get("/api/admin/topics99999", headers=admin_headers)
        assert response.status_code == 404

    def test_create_topic(self, admin_headers, db_session):
        """Test creating a topic."""
        response = client.post(
            "/api/admin/topics",
            headers=admin_headers,
            json={
                "name": "New Topic",
                "description": "New Description",
                "system_prompt": "New Prompt",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Topic"
        assert "id" in data

    def test_create_topic_with_contexts(self, admin_headers, db_session):
        """Test creating a topic with context associations."""
        # Create contexts
        ctx1 = SQLContext(
            name="Context 1", description="Desc 1", context_type="MARKDOWN"
        )
        ctx2 = SQLContext(name="Context 2", description="Desc 2", context_type="FAQ")
        db_session.add_all([ctx1, ctx2])
        db_session.commit()

        response = client.post(
            "/api/admin/topics",
            headers=admin_headers,
            json={
                "name": "Topic with Contexts",
                "description": "Description",
                "system_prompt": "Prompt",
                "context_ids": [ctx1.id, ctx2.id],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["contexts_count"] == 2

    def test_update_topic(self, admin_headers, db_session):
        """Test updating a topic."""
        topic = SQLTopic(
            name="Old Name", description="Old Desc", system_prompt="Old Prompt"
        )
        db_session.add(topic)
        db_session.commit()

        response = client.put(
            f"/api/admin/topics/{topic.id}",
            headers=admin_headers,
            json={"name": "New Name", "description": "New Desc"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["description"] == "New Desc"

    def test_update_topic_contexts(self, admin_headers, db_session):
        """Test updating topic context associations."""
        topic = SQLTopic(name="Topic", description="Desc", system_prompt="Prompt")
        ctx1 = SQLContext(
            name="Context 1", description="Desc 1", context_type="MARKDOWN"
        )
        ctx2 = SQLContext(name="Context 2", description="Desc 2", context_type="FAQ")
        db_session.add_all([topic, ctx1, ctx2])
        db_session.commit()

        response = client.put(
            f"/api/admin/topics/{topic.id}",
            headers=admin_headers,
            json={"context_ids": [ctx1.id, ctx2.id]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["contexts_count"] == 2

    def test_delete_topic(self, admin_headers, db_session):
        """Test deleting a topic."""
        topic = SQLTopic(name="To Delete", description="Desc", system_prompt="Prompt")
        db_session.add(topic)
        db_session.commit()
        topic_id = topic.id

        response = client.delete(f"/api/admin/topics/{topic_id}", headers=admin_headers)
        assert response.status_code == 204

        # Verify deletion
        deleted_topic = db_session.query(SQLTopic).filter_by(id=topic_id).first()
        assert deleted_topic is None

    def test_delete_topic_not_found(self, admin_headers):
        """Test deleting non-existent topic."""
        response = client.delete("/api/admin/topics99999", headers=admin_headers)
        assert response.status_code == 404


class TestTopicsAdminSlugUniqueness:
    """Test slug uniqueness handling in admin operations."""

    def test_create_topic_with_custom_slug(self, admin_headers, db_session):
        """Test creating a topic with a custom slug."""
        response = client.post(
            "/api/admin/topics",
            headers=admin_headers,
            json={
                "name": "Custom Slug Topic",
                "slug": "my-custom-slug",
                "description": "Description",
                "system_prompt": "Prompt",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["slug"] == "my-custom-slug"

    def test_create_topic_with_duplicate_slug_auto_resolves(
        self, admin_headers, db_session
    ):
        """Test that creating a topic with duplicate slug auto-resolves using ensure_unique_slug."""
        # Create first topic
        topic1 = SQLTopic(
            name="First Topic",
            slug="duplicate-slug",
            description="Desc",
            system_prompt="Prompt",
        )
        db_session.add(topic1)
        db_session.commit()

        # Try to create second topic with same slug
        response = client.post(
            "/api/admin/topics",
            headers=admin_headers,
            json={
                "name": "Second Topic",
                "slug": "duplicate-slug",
                "description": "Description",
                "system_prompt": "Prompt",
            },
        )
        assert response.status_code == 201
        data = response.json()
        # Should auto-resolve to unique slug (e.g., duplicate-slug-2)
        assert data["slug"] != "duplicate-slug"
        assert data["slug"].startswith("duplicate-slug")

    def test_update_topic_slug_to_duplicate_returns_409(
        self, admin_headers, db_session
    ):
        """Test that updating a topic slug to an existing slug returns 409 Conflict."""
        # Create two topics
        topic1 = SQLTopic(
            name="Topic 1", slug="slug-one", description="Desc", system_prompt="Prompt"
        )
        topic2 = SQLTopic(
            name="Topic 2", slug="slug-two", description="Desc", system_prompt="Prompt"
        )
        db_session.add_all([topic1, topic2])
        db_session.commit()

        # Try to update topic2 slug to topic1's slug
        response = client.put(
            f"/api/admin/topics/{topic2.id}",
            headers=admin_headers,
            json={"slug": "slug-one"},
        )
        assert response.status_code == 409
        assert "already in use" in response.json()["detail"]

    def test_update_topic_slug_to_same_value_succeeds(self, admin_headers, db_session):
        """Test that updating a topic slug to its current value succeeds."""
        topic = SQLTopic(
            name="Topic",
            slug="existing-slug",
            description="Desc",
            system_prompt="Prompt",
        )
        db_session.add(topic)
        db_session.commit()

        response = client.put(
            f"/api/admin/topics/{topic.id}",
            headers=admin_headers,
            json={"slug": "existing-slug", "name": "Updated Name"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "existing-slug"
        assert data["name"] == "Updated Name"

    def test_update_topic_slug_to_new_unique_value_succeeds(
        self, admin_headers, db_session
    ):
        """Test that updating a topic slug to a new unique value succeeds."""
        topic = SQLTopic(
            name="Topic", slug="old-slug", description="Desc", system_prompt="Prompt"
        )
        db_session.add(topic)
        db_session.commit()

        response = client.put(
            f"/api/admin/topics/{topic.id}",
            headers=admin_headers,
            json={"slug": "new-unique-slug"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "new-unique-slug"


class TestTopicsDatetimeSerialization:
    """Test AdminTopicOut datetime field serialization."""

    def test_admin_topic_out_datetime_serialization_format(
        self, admin_headers, db_session
    ):
        """Test created_at and updated_at are serialized as ISO 8601 strings with timezone."""
        topic = SQLTopic(
            name="Test Topic",
            description="Test Description",
            system_prompt="Test Prompt",
        )
        db_session.add(topic)
        db_session.commit()

        response = client.get(f"/api/admin/topics/{topic.id}", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()

        assert "created_at" in data
        assert "updated_at" in data
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)

        created_dt = datetime.fromisoformat(data["created_at"])
        updated_dt = datetime.fromisoformat(data["updated_at"])
        assert created_dt.tzinfo is not None
        assert updated_dt.tzinfo is not None
