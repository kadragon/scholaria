"""
Tests for FastAPI Context Write API (POST, PUT, DELETE).
"""

import io
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.auth.utils import pwd_context
from api.main import app
from api.models.base import Base, get_db
from api.models.context import Context as SQLContext
from api.models.context import ContextItem as SQLContextItem
from api.models.topic import Topic as SQLTopic
from api.models.user import User as SQLUser

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_write.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            try:
                db.execute(table.delete())
            except Exception:
                pass
        db.commit()
        db.close()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_headers(client, db_session):
    """Create an admin user and return Authorization headers."""
    password = "AdminPass123!"
    admin = SQLUser(
        username="admin",
        email="admin@example.com",
        password=pwd_context.hash(password),
        is_active=True,
        is_staff=True,
        is_superuser=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    response = client.post(
        "/api/auth/login",
        data={"username": admin.username, "password": password},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_topic(db_session):
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

    def test_create_markdown_context(self, client, db_session):
        """Test creating a Markdown context with original_content."""
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

        context = db_session.query(SQLContext).filter_by(id=data["id"]).first()
        assert context is not None
        assert context.original_content == markdown_content

    def test_create_faq_context(self, client, db_session):
        """Test creating a FAQ context (no content initially)."""
        response = client.post(
            "/api/contexts",
            data={
                "name": "Test FAQ",
                "description": "Test FAQ context",
                "context_type": "FAQ",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test FAQ"
        assert data["context_type"] == "FAQ"
        assert data["chunk_count"] == 0

    def test_create_pdf_context_without_file_fails(self, client):
        """Test creating a PDF context without file upload fails."""
        response = client.post(
            "/api/contexts",
            data={
                "name": "Test PDF",
                "description": "Test PDF context",
                "context_type": "PDF",
            },
        )

        assert response.status_code == 400
        assert "file" in response.json()["detail"].lower()

    @patch("rag.ingestion.parsers.PDFParser.parse_file")
    def test_create_pdf_context_with_file(self, mock_parse_pdf, client, db_session):
        """Test creating a PDF context with file upload."""
        mock_parse_pdf.return_value = "This is extracted PDF text."

        pdf_content = b"%PDF-1.4\n%fake pdf content"
        response = client.post(
            "/api/contexts",
            data={
                "name": "Test PDF",
                "description": "Test PDF context",
                "context_type": "PDF",
            },
            files={"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test PDF"
        assert data["context_type"] == "PDF"
        assert data["processing_status"] == "PROCESSING"

        context = db_session.query(SQLContext).filter_by(id=data["id"]).first()
        assert context is not None
        assert context.processing_status == "PROCESSING"

    def test_create_context_missing_name_fails(self, client):
        """Test creating context without name fails validation."""
        response = client.post(
            "/api/contexts",
            data={
                "description": "Test description",
                "context_type": "MARKDOWN",
            },
        )

        assert response.status_code == 422

    def test_create_context_invalid_type_fails(self, client):
        """Test creating context with invalid type fails."""
        response = client.post(
            "/api/contexts",
            data={
                "name": "Test",
                "description": "Test description",
                "context_type": "INVALID",
            },
        )

        assert response.status_code == 422


class TestUpdateContext:
    """Tests for PUT/PATCH /api/contexts/{id} endpoint."""

    @pytest.fixture
    def sample_context(self, db_session):
        context = SQLContext(
            name="Original Name",
            description="Original description",
            context_type="MARKDOWN",
            original_content="# Original",
            processing_status="COMPLETED",
        )
        db_session.add(context)
        db_session.commit()
        db_session.refresh(context)
        return context

    def test_update_context_name_and_description(
        self, client, db_session, sample_context
    ):
        """Test updating context name and description."""
        response = client.put(
            f"/api/contexts/{sample_context.id}",
            json={
                "name": "Updated Name",
                "description": "Updated description",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated description"

        db_session.refresh(sample_context)
        assert sample_context.name == "Updated Name"

    def test_update_context_original_content(self, client, db_session, sample_context):
        """Test updating original_content for Markdown context."""
        new_content = "# Updated\n\nNew content."
        response = client.patch(
            f"/api/contexts/{sample_context.id}",
            json={"original_content": new_content},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["original_content"] == new_content

    def test_update_nonexistent_context_fails(self, client):
        """Test updating nonexistent context returns 404."""
        response = client.put(
            "/api/contexts/99999",
            json={
                "name": "Test",
                "description": "Test",
            },
        )

        assert response.status_code == 404


class TestDeleteContext:
    """Tests for DELETE /api/contexts/{id} endpoint."""

    @pytest.fixture
    def sample_context_with_items(self, db_session):
        context = SQLContext(
            name="Test Context",
            description="Test description",
            context_type="FAQ",
        )
        db_session.add(context)
        db_session.commit()
        db_session.refresh(context)

        item = SQLContextItem(
            title="Test Q&A",
            content="Test content",
            context_id=context.id,
        )
        db_session.add(item)
        db_session.commit()
        return context

    def test_delete_context(self, client, db_session, sample_context_with_items):
        """Test deleting a context."""
        context_id = sample_context_with_items.id

        response = client.delete(f"/api/contexts/{context_id}")

        assert response.status_code == 204

        context = db_session.query(SQLContext).filter_by(id=context_id).first()
        assert context is None

        items = db_session.query(SQLContextItem).filter_by(context_id=context_id).all()
        assert len(items) == 0

    def test_delete_nonexistent_context_fails(self, client):
        """Test deleting nonexistent context returns 404."""
        response = client.delete("/api/contexts/99999")

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

    def test_add_faq_qa(self, client, db_session, faq_context):
        """Test adding a Q&A pair to FAQ context."""
        response = client.post(
            f"/api/contexts/{faq_context.id}/qa",
            json={
                "title": "What is RAG?",
                "content": "RAG stands for Retrieval-Augmented Generation.",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "What is RAG?"
        assert data["content"] == "RAG stands for Retrieval-Augmented Generation."

        items = (
            db_session.query(SQLContextItem).filter_by(context_id=faq_context.id).all()
        )
        assert len(items) == 1
        assert items[0].title == "What is RAG?"

    def test_add_qa_to_nonexistent_context_fails(self, client):
        """Test adding Q&A to nonexistent context fails."""
        response = client.post(
            "/api/contexts/99999/qa",
            json={
                "title": "Test",
                "content": "Test content",
            },
        )

        assert response.status_code == 404

    def test_add_qa_to_non_faq_context_fails(self, client, db_session):
        """Test adding Q&A to non-FAQ context fails."""
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
            json={
                "title": "Test",
                "content": "Test content",
            },
        )

        assert response.status_code == 400
        assert "FAQ" in response.json()["detail"]


class TestFileUploadValidation:
    """Tests for file upload validation."""

    def test_upload_non_pdf_file_fails(self, client):
        """Test uploading non-PDF file to PDF context fails."""
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
        )

        assert response.status_code == 400
        assert "pdf" in response.json()["detail"].lower()

    @patch("api.routers.contexts.MAX_UPLOAD_SIZE", 100)
    def test_upload_file_too_large_fails(self, client):
        """Test uploading file larger than limit fails."""
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
        )

        assert response.status_code == 413
