"""Tests for Contexts Admin API."""

from datetime import datetime

from fastapi.testclient import TestClient

from backend.main import app
from backend.models.context import Context as SQLContext

client = TestClient(app)


class TestContextsAdminList:
    """Test Contexts Admin list endpoint."""

    def test_list_contexts_requires_admin(self):
        """Test that listing contexts requires admin authentication."""
        response = client.get("/api/admin/contexts")
        assert response.status_code == 401

    def test_list_contexts_empty(self, admin_headers, db_session):
        """Test listing contexts when database is empty."""
        response = client.get("/api/admin/contexts", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert data["data"] == []
        assert data["total"] == 0

    def test_list_contexts_with_data(self, admin_headers, db_session):
        """Test listing contexts with existing data."""
        ctx1 = SQLContext(
            name="Context 1",
            description="Description 1",
            context_type="MARKDOWN",
            original_content="# Content 1",
            chunk_count=5,
        )
        ctx2 = SQLContext(
            name="Context 2",
            description="Description 2",
            context_type="PDF",
            chunk_count=3,
        )
        db_session.add_all([ctx1, ctx2])
        db_session.commit()

        response = client.get("/api/admin/contexts", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["total"] == 2
        assert data["data"][0]["name"] == "Context 1"
        assert data["data"][0]["context_type"] == "MARKDOWN"

    def test_list_contexts_with_filter(self, admin_headers, db_session):
        """Test filtering contexts by type."""
        ctx1 = SQLContext(
            name="Markdown Doc",
            description="Desc",
            context_type="MARKDOWN",
        )
        ctx2 = SQLContext(
            name="PDF Doc",
            description="Desc",
            context_type="PDF",
        )
        db_session.add_all([ctx1, ctx2])
        db_session.commit()

        response = client.get(
            "/api/admin/contexts",
            params={"filter": '{"context_type": "MARKDOWN"}'},
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["context_type"] == "MARKDOWN"

    def test_list_contexts_with_pagination(self, admin_headers, db_session):
        """Test pagination."""
        for i in range(5):
            ctx = SQLContext(
                name=f"Context {i}",
                description="Desc",
                context_type="MARKDOWN",
            )
            db_session.add(ctx)
        db_session.commit()

        response = client.get(
            "/api/admin/contexts",
            params={"skip": 2, "limit": 2},
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["total"] == 5


class TestContextsAdminCRUD:
    """Test Contexts Admin CRUD operations."""

    def test_get_context(self, admin_headers, db_session):
        """Test getting a single context."""
        ctx = SQLContext(
            name="Test Context",
            description="Test Description",
            context_type="MARKDOWN",
            original_content="# Test",
        )
        db_session.add(ctx)
        db_session.commit()

        response = client.get(f"/api/admin/contexts/{ctx.id}", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Context"
        assert data["context_type"] == "MARKDOWN"

    def test_get_context_not_found(self, admin_headers):
        """Test getting non-existent context."""
        response = client.get("/api/admin/contexts99999", headers=admin_headers)
        assert response.status_code == 404

    def test_create_markdown_context(self, admin_headers, db_session):
        """Test creating a Markdown context."""
        response = client.post(
            "/api/admin/contexts",
            headers=admin_headers,
            data={
                "name": "New Markdown",
                "description": "Description",
                "context_type": "MARKDOWN",
                "original_content": "# Markdown Content",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Markdown"
        assert data["context_type"] == "MARKDOWN"
        assert "id" in data

    def test_create_faq_context(self, admin_headers, db_session):
        """Test creating a FAQ context."""
        response = client.post(
            "/api/admin/contexts",
            headers=admin_headers,
            data={
                "name": "New FAQ",
                "description": "FAQ Description",
                "context_type": "FAQ",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New FAQ"
        assert data["context_type"] == "FAQ"

    def test_update_context(self, admin_headers, db_session):
        """Test updating a context."""
        ctx = SQLContext(
            name="Old Name",
            description="Old Desc",
            context_type="MARKDOWN",
        )
        db_session.add(ctx)
        db_session.commit()

        response = client.put(
            f"/api/admin/contexts/{ctx.id}",
            headers=admin_headers,
            json={
                "name": "New Name",
                "description": "New Desc",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["description"] == "New Desc"

    def test_delete_context(self, admin_headers, db_session):
        """Test deleting a context."""
        ctx = SQLContext(
            name="To Delete",
            description="Desc",
            context_type="MARKDOWN",
        )
        db_session.add(ctx)
        db_session.commit()
        ctx_id = ctx.id

        response = client.delete(f"/api/admin/contexts/{ctx_id}", headers=admin_headers)
        assert response.status_code == 204

        # Verify deletion
        deleted_ctx = db_session.query(SQLContext).filter_by(id=ctx_id).first()
        assert deleted_ctx is None

    def test_delete_context_not_found(self, admin_headers):
        """Test deleting non-existent context."""
        response = client.delete("/api/admin/contexts99999", headers=admin_headers)
        assert response.status_code == 404


class TestContextItemUpdate:
    """Test ContextItem update endpoint."""

    def test_update_context_item_not_found(self, admin_headers, db_session):
        """Test updating non-existent context item."""
        ctx = SQLContext(
            name="Test Context",
            description="Test Description",
            context_type="MARKDOWN",
            chunk_count=0,
        )
        db_session.add(ctx)
        db_session.commit()

        response = client.patch(
            f"/api/contexts/{ctx.id}/items/99999",
            headers=admin_headers,
            json={"content": "New content"},
        )
        assert response.status_code == 404

    def test_update_context_item_validation_empty_content(
        self, admin_headers, db_session, monkeypatch
    ):
        """Test validation error for empty content."""
        from unittest.mock import Mock

        from backend.models.context import ContextItem

        mock_task = Mock()
        monkeypatch.setattr(
            "backend.tasks.embeddings.regenerate_embedding_task", mock_task
        )

        ctx = SQLContext(
            name="Test",
            description="Test",
            context_type="MARKDOWN",
            chunk_count=1,
        )
        db_session.add(ctx)
        db_session.commit()

        item = ContextItem(
            context_id=ctx.id,
            title="Original Title",
            content="Original",
        )
        db_session.add(item)
        db_session.commit()

        response = client.patch(
            f"/api/contexts/{ctx.id}/items/{item.id}",
            headers=admin_headers,
            json={"content": ""},
        )
        assert response.status_code == 422

    def test_update_context_item_content_success(
        self, admin_headers, db_session, monkeypatch
    ):
        """Test successful content update."""
        from unittest.mock import Mock

        from backend.models.context import ContextItem

        mock_task = Mock()
        monkeypatch.setattr(
            "backend.tasks.embeddings.regenerate_embedding_task", mock_task
        )

        ctx = SQLContext(
            name="Test",
            description="Test",
            context_type="MARKDOWN",
            chunk_count=1,
        )
        db_session.add(ctx)
        db_session.commit()

        item = ContextItem(
            context_id=ctx.id,
            title="Original Title",
            content="Original content",
        )
        db_session.add(item)
        db_session.commit()
        item_id = item.id

        response = client.patch(
            f"/api/contexts/{ctx.id}/items/{item_id}",
            headers=admin_headers,
            json={"content": "Updated content"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated content"
        assert data["id"] == item_id

        # Verify DB update
        db_session.expire_all()
        updated_item = db_session.query(ContextItem).filter_by(id=item_id).first()
        assert updated_item.content == "Updated content"

    def test_update_context_item_embedding_regeneration(
        self, admin_headers, db_session, monkeypatch
    ):
        """Test that content update triggers embedding regeneration."""
        from unittest.mock import Mock

        from backend.models.context import ContextItem

        mock_task = Mock()
        monkeypatch.setattr(
            "backend.tasks.embeddings.regenerate_embedding_task", mock_task
        )

        ctx = SQLContext(
            name="Test",
            description="Test",
            context_type="MARKDOWN",
            chunk_count=1,
        )
        db_session.add(ctx)
        db_session.commit()

        item = ContextItem(
            context_id=ctx.id,
            title="Original Title",
            content="Original content",
        )
        db_session.add(item)
        db_session.commit()
        item_id = item.id

        response = client.patch(
            f"/api/contexts/{ctx.id}/items/{item_id}",
            headers=admin_headers,
            json={"content": "New content for embedding"},
        )
        assert response.status_code == 200

        mock_task.delay.assert_called_once_with(item_id)

        db_session.expire_all()
        updated_item = db_session.query(ContextItem).filter_by(id=item_id).first()
        assert updated_item.content == "New content for embedding"

    def test_update_context_item_order_index_success(self, admin_headers, db_session):
        """Test updating context item order_index successfully."""
        from backend.models.context import ContextItem

        ctx = SQLContext(
            name="Test Context",
            description="Test",
            context_type="MARKDOWN",
        )
        db_session.add(ctx)
        db_session.commit()

        item1 = ContextItem(
            title="Item 1",
            content="Content 1",
            context_id=ctx.id,
            order_index=0,
        )
        item2 = ContextItem(
            title="Item 2",
            content="Content 2",
            context_id=ctx.id,
            order_index=1,
        )
        db_session.add_all([item1, item2])
        db_session.commit()

        # Update item1 to order_index=5
        response = client.patch(
            f"/api/admin/contexts/{ctx.id}/items/{item1.id}",
            json={"order_index": 5},
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item1.id
        assert data["order_index"] == 5

        # Verify in DB
        db_session.expire_all()
        updated = db_session.query(ContextItem).filter_by(id=item1.id).first()
        assert updated.order_index == 5


class TestContextsDatetimeSerialization:
    """Test AdminContextOut datetime field serialization."""

    def test_admin_context_out_datetime_serialization_format(
        self, admin_headers, db_session
    ):
        """Test created_at and updated_at are serialized as ISO 8601 strings with timezone."""
        context = SQLContext(
            name="Test Context",
            description="Test Description",
            context_type="MARKDOWN",
            original_content="# Test Content",
            chunk_count=1,
        )
        db_session.add(context)
        db_session.commit()

        response = client.get(
            f"/api/admin/contexts/{context.id}", headers=admin_headers
        )
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
