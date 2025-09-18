from unittest.mock import Mock, patch

from django.test import TestCase

from rag.models import Context, ContextItem
from rag.tasks import ingest_markdown_document, ingest_pdf_document, process_document


class DocumentProcessingTaskTest(TestCase):
    def setUp(self):
        self.context = Context.objects.create(
            name="Test Context",
            description="Test context for document processing",
            context_type="PDF",
        )

    @patch("rag.tasks.ingest_pdf_document.delay")
    def test_process_document_pdf_delegates_to_pdf_task(self, mock_pdf_task):
        """Test that PDF documents are delegated to PDF ingestion task."""
        mock_pdf_task.return_value = Mock(id="task-123")

        result = process_document(
            context_id=self.context.id,
            file_path="/path/to/document.pdf",
            title="Test PDF",
        )

        # Verify PDF task was called
        mock_pdf_task.assert_called_once_with(
            self.context.id, "/path/to/document.pdf", "Test PDF"
        )

        # Verify result is the task ID
        self.assertEqual(result, "task-123")

    @patch("rag.tasks.ingest_markdown_document.delay")
    def test_process_document_markdown_delegates_to_markdown_task(self, mock_md_task):
        """Test that Markdown documents are delegated to Markdown ingestion task."""
        mock_md_task.return_value = Mock(id="task-456")

        # Update context to markdown type
        self.context.context_type = "MARKDOWN"
        self.context.save()

        result = process_document(
            context_id=self.context.id,
            file_path="/path/to/document.md",
            title="Test Markdown",
        )

        # Verify Markdown task was called
        mock_md_task.assert_called_once_with(
            self.context.id, "/path/to/document.md", "Test Markdown"
        )

        # Verify result is the task ID
        self.assertEqual(result, "task-456")

    def test_process_document_unsupported_type_raises_error(self):
        """Test that unsupported document types raise ValueError."""
        # Create context with unsupported type
        unsupported_context = Context.objects.create(
            name="Unsupported Context",
            description="Test context with unsupported type",
            context_type="FAQ",  # Not yet supported
        )

        with self.assertRaises(ValueError) as cm:
            process_document(
                context_id=unsupported_context.id,
                file_path="/path/to/document.txt",
                title="Test Document",
            )

        self.assertIn("Unsupported context type", str(cm.exception))


class PDFIngestionTaskTest(TestCase):
    def setUp(self):
        self.context = Context.objects.create(
            name="PDF Context",
            description="Test context for PDF ingestion",
            context_type="PDF",
        )

    @patch("rag.tasks.PDFParser")
    @patch("rag.tasks.TextChunker")
    def test_ingest_pdf_document_creates_context_items(
        self, mock_chunker_class, mock_parser_class
    ):
        """Test that PDF ingestion creates ContextItem objects from chunks."""
        # Mock parser
        mock_parser = Mock()
        mock_parser.parse_file.return_value = "This is extracted PDF content."
        mock_parser_class.return_value = mock_parser

        # Mock chunker
        mock_chunker = Mock()
        mock_chunker.chunk_text.return_value = [
            "This is extracted",
            "extracted PDF content.",
        ]
        mock_chunker_class.return_value = mock_chunker

        # Run the task
        result = ingest_pdf_document(
            context_id=self.context.id,
            file_path="/path/to/test.pdf",
            title="Test PDF Document",
        )

        # Verify parser was called
        mock_parser.parse_file.assert_called_once_with("/path/to/test.pdf")

        # Verify chunker was called
        mock_chunker.chunk_text.assert_called_once_with(
            "This is extracted PDF content."
        )

        # Verify ContextItems were created
        context_items = ContextItem.objects.filter(context=self.context)
        self.assertEqual(context_items.count(), 2)

        # Check first item
        item1 = context_items.first()
        assert item1 is not None  # For mypy
        self.assertEqual(item1.title, "Test PDF Document - Chunk 1")
        self.assertEqual(item1.content, "This is extracted")
        self.assertEqual(item1.file_path, "/path/to/test.pdf")

        # Check second item
        item2 = context_items.last()
        assert item2 is not None  # For mypy
        self.assertEqual(item2.title, "Test PDF Document - Chunk 2")
        self.assertEqual(item2.content, "extracted PDF content.")

        # Verify return value
        self.assertEqual(result, 2)  # Number of chunks created

    @patch("rag.tasks.PDFParser")
    def test_ingest_pdf_document_with_empty_content(self, mock_parser_class):
        """Test PDF ingestion with empty content creates no items."""
        # Mock parser returning empty content
        mock_parser = Mock()
        mock_parser.parse_file.return_value = ""
        mock_parser_class.return_value = mock_parser

        result = ingest_pdf_document(
            context_id=self.context.id,
            file_path="/path/to/empty.pdf",
            title="Empty PDF",
        )

        # Verify no ContextItems were created
        self.assertEqual(ContextItem.objects.filter(context=self.context).count(), 0)
        self.assertEqual(result, 0)

    def test_ingest_pdf_document_nonexistent_context_raises_error(self):
        """Test that non-existent context raises DoesNotExist error."""
        with self.assertRaises(Context.DoesNotExist):
            ingest_pdf_document(
                context_id=99999, file_path="/path/to/test.pdf", title="Test PDF"
            )


class MarkdownIngestionTaskTest(TestCase):
    def setUp(self):
        self.context = Context.objects.create(
            name="Markdown Context",
            description="Test context for Markdown ingestion",
            context_type="MARKDOWN",
        )

    @patch("rag.tasks.MarkdownParser")
    @patch("rag.tasks.TextChunker")
    def test_ingest_markdown_document_creates_context_items(
        self, mock_chunker_class, mock_parser_class
    ):
        """Test that Markdown ingestion creates ContextItem objects from chunks."""
        # Mock parser
        mock_parser = Mock()
        mock_parser.parse_file.return_value = "# Test\n\nThis is markdown content."
        mock_parser_class.return_value = mock_parser

        # Mock chunker
        mock_chunker = Mock()
        mock_chunker.chunk_text.return_value = [
            "# Test\n\nThis is",
            "This is markdown content.",
        ]
        mock_chunker_class.return_value = mock_chunker

        # Run the task
        result = ingest_markdown_document(
            context_id=self.context.id,
            file_path="/path/to/test.md",
            title="Test Markdown Document",
        )

        # Verify parser was called
        mock_parser.parse_file.assert_called_once_with("/path/to/test.md")

        # Verify chunker was called
        mock_chunker.chunk_text.assert_called_once_with(
            "# Test\n\nThis is markdown content."
        )

        # Verify ContextItems were created
        context_items = ContextItem.objects.filter(context=self.context)
        self.assertEqual(context_items.count(), 2)

        # Check items
        item1 = context_items.first()
        assert item1 is not None  # For mypy
        self.assertEqual(item1.title, "Test Markdown Document - Chunk 1")
        self.assertEqual(item1.content, "# Test\n\nThis is")

        # Verify return value
        self.assertEqual(result, 2)
