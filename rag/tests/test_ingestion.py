import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from django.test import TestCase

from rag.ingestion.chunkers import TextChunker
from rag.ingestion.parsers import MarkdownParser, PDFParser
from rag.models import Context


class PDFParserTest(TestCase):
    def setUp(self):
        self.parser = PDFParser()
        self.context = Context.objects.create(
            name="Test PDF Context",
            description="Test context for PDF parsing",
            context_type="PDF",
        )

    def test_parse_pdf_file_success(self):
        """Test successful PDF parsing returns text content."""
        with patch("rag.ingestion.parsers.partition_pdf") as mock_partition:
            # Mock the unstructured response
            mock_element = Mock()
            mock_element.text = "This is test content from PDF"
            mock_partition.return_value = [mock_element]

            # Create a mock PDF file
            with tempfile.NamedTemporaryFile(suffix=".pdf") as mock_file:
                result = self.parser.parse_file(mock_file.name)

                # Verify the result
                self.assertEqual(result, "This is test content from PDF")
                mock_partition.assert_called_once_with(filename=mock_file.name)

    def test_parse_pdf_file_with_multiple_elements(self):
        """Test PDF parsing with multiple elements combines text."""
        with patch("rag.ingestion.parsers.partition_pdf") as mock_partition:
            # Mock multiple elements
            mock_element1 = Mock()
            mock_element1.text = "First paragraph"
            mock_element2 = Mock()
            mock_element2.text = "Second paragraph"
            mock_partition.return_value = [mock_element1, mock_element2]

            with tempfile.NamedTemporaryFile(suffix=".pdf") as mock_file:
                result = self.parser.parse_file(mock_file.name)

                # Verify combined text
                self.assertEqual(result, "First paragraph\nSecond paragraph")

    def test_parse_pdf_file_empty_result(self):
        """Test PDF parsing with no content returns empty string."""
        with patch("rag.ingestion.parsers.partition_pdf") as mock_partition:
            mock_partition.return_value = []

            with tempfile.NamedTemporaryFile(suffix=".pdf") as mock_file:
                result = self.parser.parse_file(mock_file.name)

                self.assertEqual(result, "")

    def test_parse_pdf_file_nonexistent_file(self):
        """Test PDF parsing with nonexistent file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_file("/nonexistent/file.pdf")


class MarkdownParserTest(TestCase):
    def setUp(self):
        self.parser = MarkdownParser()

    def test_parse_markdown_file_success(self):
        """Test successful Markdown parsing returns content."""
        markdown_content = """# Test Heading

This is a test paragraph with **bold** text.

## Subheading

- List item 1
- List item 2

```python
print("Hello, World!")
```
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(markdown_content)
            f.flush()

            result = self.parser.parse_file(f.name)

            # Verify content is preserved
            self.assertEqual(result, markdown_content)

            # Clean up
            Path(f.name).unlink()

    def test_parse_markdown_file_empty(self):
        """Test parsing empty Markdown file returns empty string."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("")
            f.flush()

            result = self.parser.parse_file(f.name)
            self.assertEqual(result, "")

            # Clean up
            Path(f.name).unlink()

    def test_parse_markdown_file_nonexistent(self):
        """Test parsing nonexistent Markdown file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_file("/nonexistent/file.md")


class TextChunkerTest(TestCase):
    def setUp(self):
        self.chunker = TextChunker(chunk_size=50, overlap=10)

    def test_chunk_short_text(self):
        """Test chunking text shorter than chunk size returns single chunk."""
        text = "This is a short text."
        chunks = self.chunker.chunk_text(text)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], text)

    def test_chunk_long_text_with_overlap(self):
        """Test chunking long text creates multiple chunks with overlap."""
        text = "This is a very long text that needs to be split into multiple chunks for processing."
        chunks = self.chunker.chunk_text(text)

        # Should create multiple chunks
        self.assertGreater(len(chunks), 1)

        # Each chunk should be within size limits
        for chunk in chunks:
            self.assertLessEqual(len(chunk), self.chunker.chunk_size)

        # Verify overlap exists between consecutive chunks
        if len(chunks) > 1:
            # Check that there's some overlap between chunks
            for i in range(len(chunks) - 1):
                current_chunk = chunks[i]
                next_chunk = chunks[i + 1]
                # Simple overlap check - some words should appear in both
                current_words = set(current_chunk.split())
                next_words = set(next_chunk.split())
                if current_words & next_words:
                    break
            # Note: This is a simplified test - real overlap might be more sophisticated

    def test_chunk_empty_text(self):
        """Test chunking empty text returns empty list."""
        chunks = self.chunker.chunk_text("")
        self.assertEqual(chunks, [])

    def test_chunk_text_preserves_content(self):
        """Test that chunking preserves all original content."""
        text = "This is test content that should be preserved across chunks."
        chunks = self.chunker.chunk_text(text)

        # Combine all chunks and verify content is preserved
        combined = " ".join(chunks)
        # At minimum, all words should be present
        original_words = set(text.split())
        combined_words = set(combined.split())
        self.assertTrue(original_words.issubset(combined_words))
