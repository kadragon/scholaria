"""Tests for ingestion service."""

import tempfile
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from backend.models.context import Context, ContextItem
from backend.services.ingestion import (
    delete_temp_file,
    ingest_document,
    save_uploaded_file,
)


@pytest.fixture
def test_context(db_session: Session) -> Context:
    """Create a test context."""
    context = Context(
        name="Test Context",
        description="Test description",
        context_type="PDF",
        processing_status="PENDING",
    )
    db_session.add(context)
    db_session.commit()
    db_session.refresh(context)
    return context


@pytest.fixture
def test_pdf_file() -> object:
    """Create a temporary PDF file for testing."""
    content = b"%PDF-1.4\n%Test PDF content\nHello World\n%%EOF"
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp_file.write(content)
    tmp_file.close()
    yield Path(tmp_file.name)
    Path(tmp_file.name).unlink(missing_ok=True)


@pytest.fixture
def test_markdown_file() -> object:
    """Create a temporary Markdown file for testing."""
    content = b"# Test Markdown\n\nThis is a test markdown file.\n\n## Section 1\n\nContent here."
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".md")
    tmp_file.write(content)
    tmp_file.close()
    yield Path(tmp_file.name)
    Path(tmp_file.name).unlink(missing_ok=True)


def test_save_uploaded_file():
    """Test saving uploaded file content."""
    content = b"Test file content"
    file_path = save_uploaded_file(content, suffix=".txt")

    assert file_path.exists()
    assert file_path.read_bytes() == content

    delete_temp_file(file_path)
    assert not file_path.exists()


def test_delete_temp_file_nonexistent():
    """Test deleting a non-existent file doesn't raise error."""
    file_path = Path("/tmp/nonexistent_file.txt")
    delete_temp_file(file_path)


def test_ingest_markdown_document(
    db_session: Session, test_context: Context, test_markdown_file: Path
):
    """Test ingesting a Markdown document."""
    test_context.context_type = "MARKDOWN"
    db_session.commit()

    num_chunks = ingest_document(
        db=db_session,
        context_id=test_context.id,
        file_path=str(test_markdown_file),
        title="Test Markdown",
        context_type="MARKDOWN",
    )

    assert num_chunks > 0

    context_items = (
        db_session.query(ContextItem)
        .filter(ContextItem.context_id == test_context.id)
        .all()
    )
    assert len(context_items) == num_chunks
    assert all(item.content for item in context_items)

    import json

    for item in context_items:
        if item.item_metadata:
            item_metadata = (
                json.loads(item.item_metadata)
                if isinstance(item.item_metadata, str)
                else item.item_metadata
            )
        else:
            item_metadata = {}
        assert item_metadata.get("content_type") == "markdown"


def test_ingest_document_context_not_found(
    db_session: Session, test_markdown_file: Path
):
    """Test ingestion fails when context doesn't exist."""
    with pytest.raises(ValueError, match="Context not found"):
        ingest_document(
            db=db_session,
            context_id=99999,
            file_path=str(test_markdown_file),
            title="Test",
            context_type="MARKDOWN",
        )


def test_ingest_document_unsupported_type(
    db_session: Session, test_context: Context, test_markdown_file: Path
):
    """Test ingestion fails for unsupported context type."""
    with pytest.raises(ValueError, match="Unsupported context type"):
        ingest_document(
            db=db_session,
            context_id=test_context.id,
            file_path=str(test_markdown_file),
            title="Test",
            context_type="UNSUPPORTED",
        )


def test_ingest_document_file_not_found(db_session: Session, test_context: Context):
    """Test ingestion fails when file doesn't exist."""
    test_context.context_type = "MARKDOWN"
    db_session.commit()

    with pytest.raises(FileNotFoundError):
        ingest_document(
            db=db_session,
            context_id=test_context.id,
            file_path="/nonexistent/file.md",
            title="Test",
            context_type="MARKDOWN",
        )
