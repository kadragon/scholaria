import pytest

from backend.ingestion.chunkers import WebScraperChunker


@pytest.fixture
def chunker():
    return WebScraperChunker(chunk_size=100, overlap=20)


def test_chunk_text_simple(chunker):
    text = "This is a simple test."
    result = chunker.chunk_text(text)

    assert len(result) == 1
    assert result[0] == text


def test_chunk_text_empty(chunker):
    result = chunker.chunk_text("")

    assert result == []


def test_chunk_text_with_paragraphs():
    chunker = WebScraperChunker(chunk_size=50, overlap=10)
    text = (
        "First paragraph with some content.\n\n"
        "Second paragraph with more content.\n\n"
        "Third paragraph with even more content to ensure chunking."
    )

    result = chunker.chunk_text(text)

    assert len(result) > 1
    assert all(len(chunk) <= 60 for chunk in result)


def test_chunk_text_long_content(chunker):
    text = " ".join([f"Word{i}" for i in range(100)])

    result = chunker.chunk_text(text)

    assert len(result) > 1
    for chunk in result:
        assert len(chunk) <= chunker.chunk_size
        assert chunk.strip()


def test_chunk_text_with_newlines():
    chunker = WebScraperChunker(chunk_size=50, overlap=10)
    text = (
        "Line 1 with content\n"
        "Line 2 with content\n"
        "Line 3 with content\n"
        "Line 4 with content\n"
        "Line 5 with content\n"
        "Line 6 with content"
    )

    result = chunker.chunk_text(text)

    assert len(result) > 1
    assert all(chunk.strip() for chunk in result)


def test_chunk_text_preserves_content():
    chunker = WebScraperChunker(chunk_size=50, overlap=10)
    text = "A" * 200

    result = chunker.chunk_text(text)

    recombined = "".join(chunk.strip() for chunk in result)
    assert "A" * 200 in recombined or len(recombined) >= 180
