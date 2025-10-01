"""Tests for ingestion strategies."""

import tempfile
from pathlib import Path

import pytest


def test_base_strategy_requires_implementation():
    """BaseIngestionStrategy cannot be instantiated without implementing abstract methods."""
    from backend.ingestion.strategies import BaseIngestionStrategy

    with pytest.raises(TypeError):
        BaseIngestionStrategy()  # type: ignore[abstract]


def test_pdf_strategy_chunk_only():
    """PDFIngestionStrategy chunks text correctly."""
    from backend.ingestion.strategies import PDFIngestionStrategy

    strategy = PDFIngestionStrategy()

    text = "This is a test text. " * 100
    chunks = strategy.chunk(text)

    assert isinstance(chunks, list)
    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)
    assert sum(len(chunk) for chunk in chunks) >= len(text) - (len(chunks) - 1) * 150


@pytest.fixture
def test_markdown_file() -> object:
    """Create a temporary Markdown file for testing."""
    content = b"# Header 1\n\nParagraph 1.\n\n## Header 2\n\nParagraph 2."
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".md")
    tmp_file.write(content)
    tmp_file.close()
    yield Path(tmp_file.name)
    Path(tmp_file.name).unlink(missing_ok=True)


def test_markdown_strategy_parse_and_chunk(test_markdown_file: Path):
    """MarkdownIngestionStrategy parses and chunks Markdown correctly."""
    from backend.ingestion.strategies import MarkdownIngestionStrategy

    strategy = MarkdownIngestionStrategy()

    text = strategy.parse(str(test_markdown_file))
    assert isinstance(text, str)
    assert len(text) > 0
    assert "Header 1" in text

    chunks = strategy.chunk(text)
    assert isinstance(chunks, list)
    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)


@pytest.fixture
def test_faq_file() -> object:
    """Create a temporary FAQ file for testing."""
    content = b"Q: What is Python?\nA: A programming language.\n\nQ: What is FastAPI?\nA: A web framework."
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    tmp_file.write(content)
    tmp_file.close()
    yield Path(tmp_file.name)
    Path(tmp_file.name).unlink(missing_ok=True)


def test_faq_strategy_parse_and_chunk(test_faq_file: Path):
    """FAQIngestionStrategy parses and chunks FAQ correctly."""
    from backend.ingestion.strategies import FAQIngestionStrategy

    strategy = FAQIngestionStrategy()

    text = strategy.parse(str(test_faq_file))
    assert isinstance(text, str)
    assert len(text) > 0
    assert "What is Python" in text

    chunks = strategy.chunk(text)
    assert isinstance(chunks, list)
    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)


def test_get_ingestion_strategy_pdf():
    """get_ingestion_strategy returns PDFIngestionStrategy for PDF type."""
    from backend.ingestion.strategies import (
        PDFIngestionStrategy,
        get_ingestion_strategy,
    )

    strategy = get_ingestion_strategy("PDF")
    assert isinstance(strategy, PDFIngestionStrategy)


def test_get_ingestion_strategy_markdown():
    """get_ingestion_strategy returns MarkdownIngestionStrategy for MARKDOWN type."""
    from backend.ingestion.strategies import (
        MarkdownIngestionStrategy,
        get_ingestion_strategy,
    )

    strategy = get_ingestion_strategy("MARKDOWN")
    assert isinstance(strategy, MarkdownIngestionStrategy)


def test_get_ingestion_strategy_faq():
    """get_ingestion_strategy returns FAQIngestionStrategy for FAQ type."""
    from backend.ingestion.strategies import (
        FAQIngestionStrategy,
        get_ingestion_strategy,
    )

    strategy = get_ingestion_strategy("FAQ")
    assert isinstance(strategy, FAQIngestionStrategy)


def test_get_ingestion_strategy_unsupported():
    """get_ingestion_strategy raises ValueError for unsupported type."""
    from backend.ingestion.strategies import get_ingestion_strategy

    with pytest.raises(ValueError, match="Unsupported context type"):
        get_ingestion_strategy("UNSUPPORTED")
