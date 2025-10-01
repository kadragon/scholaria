"""Tests for FastAPI Context Write API (POST, PUT, DELETE)."""

from __future__ import annotations

import io
from pathlib import Path
from unittest.mock import patch

import pytest

from backend.models.context import Context as SQLContext
from backend.models.context import ContextItem as SQLContextItem
from backend.models.topic import Topic as SQLTopic


@pytest.fixture
def sample_topic(db_session):
    """Persist a sample topic for association tests."""
    topic = SQLTopic(
        name="Test Topic",
        description="Test description",
        system_prompt="Test prompt",
    )
    db_session.add(topic)
    db_session.commit()
    db_session.refresh(topic)
    return topic


class TestCreateContext:
    """Tests for POST /api/contexts endpoint."""

    def test_create_markdown_context(self, client, db_session, admin_headers) -> None:
        markdown_content = "# Test\n\nThis is test content."
        response = client.post(
            "/api/contexts",
            data={
                "name": "Test Markdown",
                "description": "Test markdown context",
                "context_type": "MARKDOWN",
                "original_content": markdown_content,
            },
            headers=admin_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Markdown"
        assert data["context_type"] == "MARKDOWN"
        assert data["original_content"] == markdown_content
        assert data["processing_status"] == "PENDING"

        context = db_session.query(SQLContext).filter(SQLContext.id == data["id"]).one()
        assert context.original_content == markdown_content

    def test_create_faq_context(self, client, db_session, admin_headers) -> None:
        response = client.post(
            "/api/contexts",
            data={
                "name": "FAQ Context",
                "description": "FAQ description",
                "context_type": "FAQ",
            },
            headers=admin_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "FAQ Context"
        assert data["context_type"] == "FAQ"
        assert data["processing_status"] == "PENDING"

    def test_create_pdf_context_without_file_fails(self, client, admin_headers) -> None:
        response = client.post(
            "/api/contexts",
            data={
                "name": "PDF Context",
                "description": "Missing file",
                "context_type": "PDF",
            },
            headers=admin_headers,
        )

        assert response.status_code == 400
        assert "file" in response.json()["detail"].lower()

    @patch("backend.services.ingestion.delete_temp_file")
    @patch(
        "backend.services.ingestion.save_uploaded_file",
        return_value=Path("/tmp/fake.pdf"),
    )
    @patch(
        "backend.ingestion.parsers.PDFParser.parse_file",
        return_value="Parsed PDF",
    )
    @patch("backend.services.ingestion.ingest_document", return_value=2)
    def test_create_pdf_context_with_file(
        self,
        mock_ingest,
        mock_parse,
        mock_save,
        mock_delete,
        client,
        admin_headers,
    ) -> None:
        pdf_bytes = io.BytesIO(b"%PDF-1.4 test")
        response = client.post(
            "/api/contexts",
            data={
                "name": "PDF Context",
                "description": "PDF description",
                "context_type": "PDF",
            },
            files={"file": ("test.pdf", pdf_bytes, "application/pdf")},
            headers=admin_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["context_type"] == "PDF"
        assert data["processing_status"] == "COMPLETED"
        mock_ingest.assert_called_once()
        mock_parse.assert_called_once_with(str(Path("/tmp/fake.pdf")))

    def test_create_context_missing_name_fails(self, client, admin_headers) -> None:
        response = client.post(
            "/api/contexts",
            data={
                "description": "Missing name",
                "context_type": "MARKDOWN",
            },
            headers=admin_headers,
        )

        assert response.status_code == 422

    def test_create_context_invalid_type_fails(self, client, admin_headers) -> None:
        response = client.post(
            "/api/contexts",
            data={
                "name": "Invalid",
                "description": "Invalid type",
                "context_type": "INVALID",
            },
            headers=admin_headers,
        )

        assert response.status_code == 422


class TestUpdateContext:
    """Tests for PUT /api/contexts/{id} endpoint."""

    def test_update_context_name_and_description(
        self, client, db_session, sample_topic, admin_headers
    ) -> None:
        context = SQLContext(
            name="Original",
            description="Original description",
            context_type="MARKDOWN",
        )
        db_session.add(context)
        db_session.commit()
        db_session.refresh(context)

        response = client.put(
            f"/api/contexts/{context.id}",
            json={
                "name": "Updated",
                "description": "Updated description",
            },
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"
        assert data["description"] == "Updated description"

    def test_update_context_original_content(
        self, client, db_session, sample_topic, admin_headers
    ) -> None:
        context = SQLContext(
            name="Markdown Context",
            description="Test",
            context_type="MARKDOWN",
        )
        db_session.add(context)
        db_session.commit()
        db_session.refresh(context)

        response = client.put(
            f"/api/contexts/{context.id}",
            json={"original_content": "# Updated"},
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["original_content"] == "# Updated"

    def test_update_nonexistent_context_fails(self, client, admin_headers) -> None:
        response = client.put(
            "/api/contexts/99999",
            json={"name": "Updated"},
            headers=admin_headers,
        )

        assert response.status_code == 404


class TestDeleteContext:
    """Tests for DELETE /api/contexts/{id} endpoint."""

    def test_delete_context(self, client, db_session, admin_headers) -> None:
        context = SQLContext(
            name="Context to delete",
            description="Delete me",
            context_type="MARKDOWN",
        )
        db_session.add(context)
        db_session.commit()
        db_session.refresh(context)

        response = client.delete(
            f"/api/contexts/{context.id}",
            headers=admin_headers,
        )

        assert response.status_code == 204
        remaining = (
            db_session.query(SQLContext).filter(SQLContext.id == context.id).first()
        )
        assert remaining is None

        items = (
            db_session.query(SQLContextItem)
            .filter(SQLContextItem.context_id == context.id)
            .all()
        )
        assert not items

    def test_delete_nonexistent_context_fails(self, client, admin_headers) -> None:
        response = client.delete(
            "/api/contexts/99999",
            headers=admin_headers,
        )

        assert response.status_code == 404


class TestAddFAQQA:
    """Tests for POST /api/contexts/{id}/qa endpoint."""

    @pytest.fixture
    def faq_context(self, db_session):
        context = SQLContext(
            name="FAQ Context",
            description="FAQ description",
            context_type="FAQ",
        )
        db_session.add(context)
        db_session.commit()
        db_session.refresh(context)
        return context

    def test_add_faq_qa(self, client, db_session, faq_context, admin_headers) -> None:
        response = client.post(
            f"/api/contexts/{faq_context.id}/qa",
            json={
                "title": "What is RAG?",
                "content": "RAG stands for Retrieval-Augmented Generation.",
            },
            headers=admin_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "What is RAG?"

        items = (
            db_session.query(SQLContextItem)
            .filter(SQLContextItem.context_id == faq_context.id)
            .all()
        )
        assert len(items) == 1
        assert items[0].title == "What is RAG?"

    def test_add_qa_to_nonexistent_context_fails(self, client, admin_headers) -> None:
        response = client.post(
            "/api/contexts/99999/qa",
            json={"title": "Test", "content": "Test content"},
            headers=admin_headers,
        )

        assert response.status_code == 404

    def test_add_qa_to_non_faq_context_fails(
        self, client, db_session, admin_headers
    ) -> None:
        context = SQLContext(
            name="Markdown Context",
            description="Test",
            context_type="MARKDOWN",
        )
        db_session.add(context)
        db_session.commit()
        db_session.refresh(context)

        response = client.post(
            f"/api/contexts/{context.id}/qa",
            json={"title": "Test", "content": "Test content"},
            headers=admin_headers,
        )

        assert response.status_code == 400
        assert "FAQ" in response.json()["detail"]


class TestFileUploadValidation:
    """Tests for file upload validation."""

    def test_upload_non_pdf_file_fails(self, client, admin_headers) -> None:
        response = client.post(
            "/api/contexts",
            data={
                "name": "Test PDF",
                "description": "Test",
                "context_type": "PDF",
            },
            files={
                "file": (
                    "test.txt",
                    io.BytesIO(b"Not a PDF"),
                    "text/plain",
                )
            },
            headers=admin_headers,
        )

        assert response.status_code == 400
        assert "pdf" in response.json()["detail"].lower()

    @patch("backend.routers.contexts.MAX_UPLOAD_SIZE", 100)
    def test_upload_file_too_large_fails(self, client, admin_headers) -> None:
        large_content = b"x" * 200
        response = client.post(
            "/api/contexts",
            data={
                "name": "Test PDF",
                "description": "Test",
                "context_type": "PDF",
            },
            files={
                "file": (
                    "test.pdf",
                    io.BytesIO(large_content),
                    "application/pdf",
                )
            },
            headers=admin_headers,
        )

        assert response.status_code == 413
