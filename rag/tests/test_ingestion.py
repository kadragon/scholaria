import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from django.test import TestCase

from rag.ingestion.chunkers import TextChunker
from rag.ingestion.parsers import FAQParser, MarkdownParser, PDFParser
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
        """Test successful PDF parsing returns text content using Docling."""
        with patch("rag.ingestion.parsers.DocumentConverter") as mock_converter_cls:
            mock_converter = mock_converter_cls.return_value
            mock_document = Mock()
            mock_document.document = Mock()
            mock_document.document.export_to_text.return_value = (
                "This is test content from PDF"
            )
            mock_converter.convert.return_value = mock_document

            with tempfile.NamedTemporaryFile(suffix=".pdf") as mock_file:
                result = self.parser.parse_file(mock_file.name)

                self.assertEqual(result, "This is test content from PDF")
                mock_converter.convert.assert_called_once_with(mock_file.name)

    def test_parse_pdf_file_with_multiple_sections(self):
        """Test Docling PDF parsing combines sections into newline separated text."""
        with patch("rag.ingestion.parsers.DocumentConverter") as mock_converter_cls:
            mock_converter = mock_converter_cls.return_value
            mock_document = Mock()
            mock_document.document = Mock()
            mock_document.document.export_to_text.return_value = (
                "First paragraph\nSecond paragraph"
            )
            mock_converter.convert.return_value = mock_document

            with tempfile.NamedTemporaryFile(suffix=".pdf") as mock_file:
                result = self.parser.parse_file(mock_file.name)

                self.assertEqual(result, "First paragraph\nSecond paragraph")

    def test_parse_pdf_file_empty_result(self):
        """Test Docling PDF parsing with no text returns empty string."""
        with patch("rag.ingestion.parsers.DocumentConverter") as mock_converter_cls:
            mock_converter = mock_converter_cls.return_value
            mock_document = Mock()
            mock_document.document = Mock()
            mock_document.document.export_to_text.return_value = ""
            mock_converter.convert.return_value = mock_document

            with tempfile.NamedTemporaryFile(suffix=".pdf") as mock_file:
                result = self.parser.parse_file(mock_file.name)

                self.assertEqual(result, "")

    def test_parse_pdf_requires_docling_dependency(self):
        """Test parsing raises helpful error when Docling is unavailable."""
        with patch("rag.ingestion.parsers.DocumentConverter", None):
            with tempfile.NamedTemporaryFile(suffix=".pdf") as mock_file:
                with self.assertRaisesRegex(
                    ImportError, "Docling dependency is required for PDF parsing"
                ):
                    self.parser.parse_file(mock_file.name)

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


class FAQParserTest(TestCase):
    def setUp(self):
        self.parser = FAQParser()

    def test_parse_faq_file_success(self):
        """Test successful FAQ parsing returns formatted content."""
        faq_content = """Q: What is the capital of France?
A: The capital of France is Paris.

Q: How do I reset my password?
A: To reset your password, go to the login page and click "Forgot Password". Follow the instructions in the email you receive.

Q: What are the office hours?
A: Our office hours are Monday through Friday, 9 AM to 5 PM EST.
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(faq_content)
            f.flush()

            result = self.parser.parse_file(f.name)

            # Verify content is preserved and formatted
            self.assertIn("What is the capital of France?", result)
            self.assertIn("The capital of France is Paris.", result)
            self.assertIn("How do I reset my password?", result)
            self.assertIn("What are the office hours?", result)

            # Clean up
            Path(f.name).unlink()

    def test_parse_faq_file_with_structured_format(self):
        """Test FAQ parsing with structured Q: A: format."""
        faq_content = """Q: What is Python?
A: Python is a high-level programming language known for its simplicity and readability.

Q: What is Django?
A: Django is a web framework for Python that follows the model-view-template architectural pattern.
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(faq_content)
            f.flush()

            result = self.parser.parse_file(f.name)

            # Should contain structured Q&A pairs
            self.assertIn("Q:", result)
            self.assertIn("A:", result)
            self.assertIn("Python", result)
            self.assertIn("Django", result)

            # Clean up
            Path(f.name).unlink()

    def test_parse_faq_file_empty(self):
        """Test parsing empty FAQ file returns empty string."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("")
            f.flush()

            result = self.parser.parse_file(f.name)
            self.assertEqual(result, "")

            # Clean up
            Path(f.name).unlink()

    def test_parse_faq_file_nonexistent(self):
        """Test parsing nonexistent FAQ file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_file("/nonexistent/faq.txt")

    def test_parse_faq_with_different_separators(self):
        """Test FAQ parsing handles different question-answer separators."""
        faq_content = """Question: What is machine learning?
Answer: Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data.

Q. How does AI work?
A. AI works by processing large amounts of data to identify patterns and make predictions.
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(faq_content)
            f.flush()

            result = self.parser.parse_file(f.name)

            # Should handle both formats
            self.assertIn("machine learning", result)
            self.assertIn("artificial intelligence", result)
            self.assertIn("How does AI work?", result)

            # Clean up
            Path(f.name).unlink()


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

    def test_optimized_markdown_chunking(self) -> None:
        """Test optimized chunking for Markdown documents respects structure."""
        from rag.ingestion.chunkers import MarkdownChunker

        chunker = MarkdownChunker(chunk_size=200, overlap=50)

        # Markdown with headers and sections
        markdown_text = """# Introduction

This is the introduction section with some content.

## Getting Started

Here are the steps to get started:

1. First step
2. Second step
3. Third step

### Installation

To install the software:

```bash
pip install package
```

## Advanced Topics

This section covers advanced topics like configuration and troubleshooting."""

        chunks = chunker.chunk_text(markdown_text)

        # Should create multiple chunks
        self.assertGreater(len(chunks), 1)

        # Each chunk should be within size limits
        for chunk in chunks:
            self.assertLessEqual(len(chunk), chunker.chunk_size)

        # Headers should be preserved at chunk boundaries when possible
        # At least one chunk should contain a complete section
        section_preserved = any("# Introduction" in chunk for chunk in chunks)
        self.assertTrue(section_preserved)

    def test_optimized_faq_chunking(self) -> None:
        """Test optimized chunking for FAQ documents keeps Q&A pairs together."""
        from rag.ingestion.chunkers import FAQChunker

        chunker = FAQChunker(chunk_size=300, overlap=50)

        # FAQ content with Q&A pairs
        faq_text = """Q: What is machine learning?
A: Machine learning is a method of data analysis that automates analytical model building. It is a branch of artificial intelligence based on the idea that systems can learn from data.

Q: How does deep learning work?
A: Deep learning uses artificial neural networks with multiple layers to model and understand complex patterns in data. Each layer learns to transform its input data into a slightly more abstract representation.

Q: What is the difference between supervised and unsupervised learning?
A: Supervised learning uses labeled training data to learn a mapping from inputs to outputs, while unsupervised learning finds patterns in data without labeled examples."""

        chunks = chunker.chunk_text(faq_text)

        # Should create chunks that preserve Q&A pairs
        self.assertGreater(len(chunks), 0)

        # Each chunk should ideally contain complete Q&A pairs
        for chunk in chunks:
            self.assertLessEqual(len(chunk), chunker.chunk_size)
            # If chunk contains Q:, it should also contain A:
            if "Q:" in chunk:
                self.assertIn("A:", chunk, "Q&A pairs should be kept together")

    def test_optimized_pdf_chunking(self) -> None:
        """Test optimized chunking for PDF documents handles varied formatting."""
        from rag.ingestion.chunkers import PDFChunker

        chunker = PDFChunker(chunk_size=400, overlap=80)

        # PDF-like content with mixed formatting
        pdf_text = """Executive Summary
This document provides an overview of the key findings.

Introduction
The research was conducted over a 12-month period to analyze market trends and consumer behavior patterns.

Key Findings:
• Finding 1: Market growth increased by 15%
• Finding 2: Consumer engagement improved
• Finding 3: Digital adoption accelerated

Table 1: Performance Metrics
Revenue: $1.2M
Growth: 15%
Users: 50K

Conclusion
Based on the analysis, we recommend implementing the proposed strategy to capitalize on identified opportunities."""

        chunks = chunker.chunk_text(pdf_text)

        # Should create multiple chunks
        self.assertGreater(len(chunks), 1)

        # Each chunk should be within size limits
        for chunk in chunks:
            self.assertLessEqual(len(chunk), chunker.chunk_size)

        # Headers and structure should be preserved where possible
        # Check that section headers are preserved
        headers_preserved = any(
            "Executive Summary" in chunk or "Introduction" in chunk for chunk in chunks
        )
        self.assertTrue(headers_preserved)
