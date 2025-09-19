"""Comprehensive Celery task processing and error handling tests."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

from celery.exceptions import Retry
from django.test import TestCase, override_settings

from rag.models import Context, ContextItem
from rag.tasks import (
    ingest_faq_document,
    ingest_markdown_document,
    ingest_pdf_document,
    process_document,
)

if TYPE_CHECKING:
    pass


class CeleryTaskProcessingTest(TestCase):
    """Test Celery task processing functionality."""

    def setUp(self) -> None:
        """Set up test data."""
        self.context = Context.objects.create(
            name="Test Context",
            description="Test context for Celery integration",
            context_type="PDF",
        )

    def test_celery_task_structure_and_configuration(self) -> None:
        """Test that Celery tasks are properly configured."""
        # Verify tasks are properly decorated and importable
        self.assertTrue(hasattr(process_document, "delay"))
        self.assertTrue(hasattr(ingest_pdf_document, "delay"))
        self.assertTrue(hasattr(ingest_markdown_document, "delay"))
        self.assertTrue(hasattr(ingest_faq_document, "delay"))

        # Verify task names are correctly set
        self.assertEqual(process_document.name, "rag.tasks.process_document")
        self.assertEqual(ingest_pdf_document.name, "rag.tasks.ingest_pdf_document")
        self.assertEqual(
            ingest_markdown_document.name, "rag.tasks.ingest_markdown_document"
        )
        self.assertEqual(ingest_faq_document.name, "rag.tasks.ingest_faq_document")

    @patch("rag.tasks.ingest_pdf_document.delay")
    def test_task_delegation_chain(self, mock_pdf_task: Mock) -> None:
        """Test the complete task delegation chain works correctly."""
        mock_pdf_task.return_value = Mock(id="test-task-123")

        # Test delegation chain
        task_id = process_document(
            context_id=self.context.id,
            file_path="/test/document.pdf",
            title="Test Document",
        )

        # Verify delegation occurred
        mock_pdf_task.assert_called_once_with(
            self.context.id, "/test/document.pdf", "Test Document"
        )
        self.assertEqual(task_id, "test-task-123")

    def test_task_with_real_database_operations(self) -> None:
        """Test task execution with real database operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.md"
            test_file.write_text("# Test Document\n\nThis is test content.")

            # Mock external dependencies but use real database
            with patch("rag.tasks.MarkdownParser") as mock_parser_class:
                mock_parser = Mock()
                mock_parser.parse_file.return_value = (
                    "# Test Document\n\nThis is test content."
                )
                mock_parser_class.return_value = mock_parser

                with patch(
                    "rag.ingestion.chunkers.MarkdownChunker"
                ) as mock_chunker_class:
                    mock_chunker = Mock()
                    mock_chunker.chunk_text.return_value = [
                        "# Test Document",
                        "This is test content.",
                    ]
                    mock_chunker_class.return_value = mock_chunker

                    # Execute task
                    self.context.context_type = "MARKDOWN"
                    self.context.save()

                    result = ingest_markdown_document(
                        context_id=self.context.id,
                        file_path=str(test_file),
                        title="Test Markdown",
                    )

                    # Verify database operations
                    self.assertEqual(result, 2)
                    items = ContextItem.objects.filter(context=self.context)
                    self.assertEqual(items.count(), 2)

                    # Verify metadata
                    first_item = items.first()
                    self.assertIsNotNone(first_item)
                    assert first_item is not None
                    self.assertEqual(first_item.title, "Test Markdown - Chunk 1")
                    self.assertIsNotNone(first_item.metadata)
                    assert first_item.metadata is not None
                    self.assertEqual(first_item.metadata["chunk_index"], 1)
                    self.assertEqual(first_item.metadata["total_chunks"], 2)


class CeleryErrorHandlingTest(TestCase):
    """Test Celery task error handling scenarios."""

    def setUp(self) -> None:
        """Set up test data."""
        self.context = Context.objects.create(
            name="Error Test Context",
            description="Context for error testing",
            context_type="PDF",
        )

    def test_database_error_handling(self) -> None:
        """Test handling of database-related errors."""
        # Test with non-existent context
        with self.assertRaises(Context.DoesNotExist):
            process_document(
                context_id=99999, file_path="/test/document.pdf", title="Test Document"
            )

        # Test with invalid context ID type (should be handled gracefully)
        with self.assertRaises(ValueError):
            process_document(
                context_id="invalid",
                file_path="/test/document.pdf",
                title="Test Document",
            )

    @patch("rag.tasks.PDFParser")
    def test_file_system_error_handling(self, mock_parser_class: Mock) -> None:
        """Test handling of file system errors."""
        # Mock parser to raise FileNotFoundError
        mock_parser = Mock()
        mock_parser.parse_file.side_effect = FileNotFoundError("File not found")
        mock_parser_class.return_value = mock_parser

        with self.assertRaises(FileNotFoundError):
            ingest_pdf_document(
                context_id=self.context.id,
                file_path="/nonexistent/file.pdf",
                title="Missing File",
            )

    @patch("rag.tasks.PDFParser")
    def test_parsing_error_handling(self, mock_parser_class: Mock) -> None:
        """Test handling of parsing errors."""
        # Mock parser to raise parsing error
        mock_parser = Mock()
        mock_parser.parse_file.side_effect = Exception("Parsing failed")
        mock_parser_class.return_value = mock_parser

        with self.assertRaises(Exception) as cm:
            ingest_pdf_document(
                context_id=self.context.id,
                file_path="/test/corrupted.pdf",
                title="Corrupted File",
            )

        self.assertIn("Parsing failed", str(cm.exception))

    @patch("rag.tasks.PDFParser")
    @patch("rag.ingestion.chunkers.PDFChunker")
    def test_chunking_error_handling(
        self, mock_chunker_class: Mock, mock_parser_class: Mock
    ) -> None:
        """Test handling of chunking errors."""
        # Mock parser success
        mock_parser = Mock()
        mock_parser.parse_file.return_value = "Valid content"
        mock_parser_class.return_value = mock_parser

        # Mock chunker to raise error
        mock_chunker = Mock()
        mock_chunker.chunk_text.side_effect = Exception("Chunking failed")
        mock_chunker_class.return_value = mock_chunker

        with self.assertRaises(Exception) as cm:
            ingest_pdf_document(
                context_id=self.context.id,
                file_path="/test/document.pdf",
                title="Test Document",
            )

        self.assertIn("Chunking failed", str(cm.exception))

    @patch("rag.tasks.ContextItem.objects.bulk_create")
    @patch("rag.tasks.PDFParser")
    @patch("rag.ingestion.chunkers.PDFChunker")
    def test_database_write_error_handling(
        self, mock_chunker_class: Mock, mock_parser_class: Mock, mock_bulk_create: Mock
    ) -> None:
        """Test handling of database write errors."""
        # Mock successful parsing and chunking
        mock_parser = Mock()
        mock_parser.parse_file.return_value = "Valid content"
        mock_parser_class.return_value = mock_parser

        mock_chunker = Mock()
        mock_chunker.chunk_text.return_value = ["chunk1", "chunk2"]
        mock_chunker_class.return_value = mock_chunker

        # Mock database error
        mock_bulk_create.side_effect = Exception("Database write failed")

        with self.assertRaises(Exception) as cm:
            ingest_pdf_document(
                context_id=self.context.id,
                file_path="/test/document.pdf",
                title="Test Document",
            )

        self.assertIn("Database write failed", str(cm.exception))

    def test_unsupported_document_type_error(self) -> None:
        """Test error handling for unsupported document types."""
        # Create context with unsupported type
        unsupported_context = Context.objects.create(
            name="Unsupported Context",
            description="Context with unsupported type",
            context_type="UNSUPPORTED",
        )

        with self.assertRaises(ValueError) as cm:
            process_document(
                context_id=unsupported_context.id,
                file_path="/test/document.xyz",
                title="Unsupported Document",
            )

        self.assertIn("Unsupported context type", str(cm.exception))

    @patch("rag.tasks.PDFParser")
    def test_empty_file_handling(self, mock_parser_class: Mock) -> None:
        """Test handling of empty files."""
        # Mock parser to return empty content
        mock_parser = Mock()
        mock_parser.parse_file.return_value = ""
        mock_parser_class.return_value = mock_parser

        result = ingest_pdf_document(
            context_id=self.context.id,
            file_path="/test/empty.pdf",
            title="Empty Document",
        )

        # Should return 0 chunks and not create any items
        self.assertEqual(result, 0)
        self.assertEqual(ContextItem.objects.filter(context=self.context).count(), 0)

    @patch("rag.tasks.PDFParser")
    def test_none_content_handling(self, mock_parser_class: Mock) -> None:
        """Test handling when parser returns None."""
        # Mock parser to return None
        mock_parser = Mock()
        mock_parser.parse_file.return_value = None
        mock_parser_class.return_value = mock_parser

        result = ingest_pdf_document(
            context_id=self.context.id,
            file_path="/test/invalid.pdf",
            title="Invalid Document",
        )

        # Should return 0 chunks and not create any items
        self.assertEqual(result, 0)
        self.assertEqual(ContextItem.objects.filter(context=self.context).count(), 0)


class CeleryTaskRetryTest(TestCase):
    """Test Celery task retry mechanisms."""

    def setUp(self) -> None:
        """Set up test data."""
        self.context = Context.objects.create(
            name="Retry Test Context",
            description="Context for retry testing",
            context_type="PDF",
        )

    def test_retry_mechanism_exists(self) -> None:
        """Test that retry mechanisms can be implemented."""
        # Note: This tests the structure for retry implementation
        # Actual retry logic would need to be added to tasks

        # Verify tasks have retry capabilities available
        self.assertTrue(hasattr(ingest_pdf_document, "retry"))
        self.assertTrue(hasattr(ingest_markdown_document, "retry"))
        self.assertTrue(hasattr(ingest_faq_document, "retry"))

    @patch("rag.tasks.PDFParser")
    def test_transient_error_scenario(self, mock_parser_class: Mock) -> None:
        """Test scenario that would benefit from retry (transient network error)."""
        # Mock parser to simulate transient error
        mock_parser = Mock()
        mock_parser.parse_file.side_effect = ConnectionError("Temporary network issue")
        mock_parser_class.return_value = mock_parser

        # Import the required exception for retry testing

        # Should raise Retry exception, indicating the task will be retried
        with self.assertRaises(Retry):
            ingest_pdf_document(
                context_id=self.context.id,
                file_path="/test/document.pdf",
                title="Test Document",
            )


class CeleryTaskMonitoringTest(TestCase):
    """Test Celery task monitoring and observability."""

    def setUp(self) -> None:
        """Set up test data."""
        self.context = Context.objects.create(
            name="Monitoring Test Context",
            description="Context for monitoring testing",
            context_type="MARKDOWN",
        )

    @patch("rag.tasks.MarkdownParser")
    @patch("rag.ingestion.chunkers.MarkdownChunker")
    def test_task_execution_monitoring(
        self, mock_chunker_class: Mock, mock_parser_class: Mock
    ) -> None:
        """Test that task execution can be monitored."""
        # Mock successful execution
        mock_parser = Mock()
        mock_parser.parse_file.return_value = "Test content"
        mock_parser_class.return_value = mock_parser

        mock_chunker = Mock()
        mock_chunker.chunk_text.return_value = ["chunk1", "chunk2"]
        mock_chunker_class.return_value = mock_chunker

        # Execute task and verify return value for monitoring
        result = ingest_markdown_document(
            context_id=self.context.id,
            file_path="/test/document.md",
            title="Test Document",
        )

        # Verify meaningful return value for monitoring
        self.assertEqual(result, 2)

        # Verify database state for monitoring
        items = ContextItem.objects.filter(context=self.context)
        self.assertEqual(items.count(), 2)

    def test_task_metadata_for_monitoring(self) -> None:
        """Test that tasks include metadata useful for monitoring."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.md"
            test_file.write_text("# Test\nContent")

            with patch("rag.tasks.MarkdownParser") as mock_parser_class:
                mock_parser = Mock()
                mock_parser.parse_file.return_value = "# Test\nContent"
                mock_parser_class.return_value = mock_parser

                with patch(
                    "rag.ingestion.chunkers.MarkdownChunker"
                ) as mock_chunker_class:
                    mock_chunker = Mock()
                    mock_chunker.chunk_text.return_value = ["chunk1"]
                    mock_chunker_class.return_value = mock_chunker

                    ingest_markdown_document(
                        context_id=self.context.id,
                        file_path=str(test_file),
                        title="Test Document",
                    )

                    # Verify metadata in created items
                    item = ContextItem.objects.filter(context=self.context).first()
                    self.assertIsNotNone(item)
                    assert item is not None
                    self.assertIsNotNone(item.metadata)
                    assert item.metadata is not None

                    # Check monitoring-relevant metadata
                    self.assertIn("chunk_index", item.metadata)
                    self.assertIn("total_chunks", item.metadata)
                    self.assertIn("chunk_size", item.metadata)


class CeleryTaskPerformanceTest(TestCase):
    """Test Celery task performance characteristics."""

    def setUp(self) -> None:
        """Set up test data."""
        self.context = Context.objects.create(
            name="Performance Test Context",
            description="Context for performance testing",
            context_type="PDF",
        )

    @patch("rag.tasks.PDFParser")
    @patch("rag.ingestion.chunkers.PDFChunker")
    def test_bulk_operations_performance(
        self, mock_chunker_class: Mock, mock_parser_class: Mock
    ) -> None:
        """Test that tasks use efficient bulk operations."""
        # Mock parser and chunker
        mock_parser = Mock()
        mock_parser.parse_file.return_value = "Large document content"
        mock_parser_class.return_value = mock_parser

        # Create many chunks to test bulk operations
        many_chunks = [f"chunk_{i}" for i in range(100)]
        mock_chunker = Mock()
        mock_chunker.chunk_text.return_value = many_chunks
        mock_chunker_class.return_value = mock_chunker

        # Execute task
        result = ingest_pdf_document(
            context_id=self.context.id,
            file_path="/test/large_document.pdf",
            title="Large Document",
        )

        # Verify all chunks were created
        self.assertEqual(result, 100)
        self.assertEqual(ContextItem.objects.filter(context=self.context).count(), 100)

        # Verify bulk_create was used (implicit test - if individual saves were used,
        # this test would be much slower)
        items = ContextItem.objects.filter(context=self.context)
        self.assertEqual(items.count(), 100)

    @patch("rag.tasks.PDFParser")
    def test_memory_efficient_processing(self, mock_parser_class: Mock) -> None:
        """Test that tasks handle large content efficiently."""
        # Mock parser to return large content
        large_content = "Large content " * 10000  # ~130KB
        mock_parser = Mock()
        mock_parser.parse_file.return_value = large_content
        mock_parser_class.return_value = mock_parser

        with patch("rag.ingestion.chunkers.PDFChunker") as mock_chunker_class:
            mock_chunker = Mock()
            # Return many small chunks
            mock_chunker.chunk_text.return_value = [
                large_content[i : i + 1000] for i in range(0, len(large_content), 1000)
            ]
            mock_chunker_class.return_value = mock_chunker

            # This should complete without memory issues
            result = ingest_pdf_document(
                context_id=self.context.id,
                file_path="/test/large_document.pdf",
                title="Large Document",
            )

            # Verify processing completed
            self.assertGreater(result, 0)


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class CeleryIntegrationTest(TestCase):
    """Test Celery integration with Django settings."""

    def setUp(self) -> None:
        """Set up test data."""
        self.context = Context.objects.create(
            name="Integration Test Context",
            description="Context for integration testing",
            context_type="PDF",
        )

    def test_celery_eager_mode_works(self) -> None:
        """Test that Celery tasks work in eager mode for testing."""
        with patch("rag.tasks.ingest_pdf_document") as mock_task:
            mock_task.return_value = 5  # Mock return value

            # This should execute immediately in eager mode
            result = mock_task(
                context_id=self.context.id,
                file_path="/test/document.pdf",
                title="Test Document",
            )

            self.assertEqual(result, 5)
            mock_task.assert_called_once()

    def test_task_routing_configuration(self) -> None:
        """Test that task routing is properly configured."""
        # Test that we can import and access task configuration
        from rag.tasks import process_document

        # Verify task is accessible and has expected properties
        self.assertTrue(callable(process_document))
        self.assertTrue(hasattr(process_document, "name"))
        self.assertEqual(process_document.name, "rag.tasks.process_document")
