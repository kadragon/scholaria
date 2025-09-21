from typing import cast
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile, UploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.datastructures import MultiValueDict

from rag.models import Context


class PDFUploadWorkflowTest(TestCase):
    """Test the new PDF upload → parse → chunk → discard file workflow."""

    def test_pdf_upload_should_parse_and_discard_file(self):
        """
        Test that PDF upload immediately parses content, stores in Context.original_content,
        creates chunks, and does NOT store the file anywhere.
        """
        # Create a mock PDF file
        pdf_content = b"%PDF-1.4\nMock PDF content"
        uploaded_file = SimpleUploadedFile(
            "test.pdf", pdf_content, content_type="application/pdf"
        )

        # Mock the PDF parser to return text content
        with patch("rag.ingestion.parsers.PDFParser.parse_file") as mock_parse:
            mock_parse.return_value = "Parsed PDF text content"

            # Create a context with PDF upload (this should trigger the new workflow)
            context = Context.objects.create(
                name="Test PDF Context",
                description="Test context for PDF workflow",
                context_type="PDF",
            )

            # Simulate the new upload workflow
            # This should:
            # 1. Parse the PDF content
            # 2. Store in context.original_content
            # 3. Create chunks in ContextItem
            # 4. NOT store the file

            # Process the PDF upload using the new workflow
            result = context.process_pdf_upload(uploaded_file)

            # Verify the workflow results
            self.assertTrue(result)

            # Refresh from database
            context.refresh_from_db()

            # Should store parsed content in original_content
            self.assertEqual(context.original_content, "Parsed PDF text content")

            # Should update processing status
            self.assertEqual(context.processing_status, "COMPLETED")

            # Should create chunks (context items)
            chunks = context.items.all()
            self.assertTrue(chunks.exists())

            # Should NOT store the uploaded file anywhere
            for chunk in chunks:
                self.assertFalse(chunk.uploaded_file)  # Empty FieldFile
                self.assertIsNone(chunk.file_path)


class PDFAdminWorkflowTest(TestCase):
    """Test the admin interface for PDF upload workflow."""

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username="admin", password="admin", is_staff=True, is_superuser=True
        )
        self.client.login(username="admin", password="admin")

    def test_admin_context_form_has_file_upload_field(self):
        """Test that the Context admin form includes file upload field."""
        url = reverse("admin:rag_context_add")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "uploaded_file")
        self.assertContains(
            response, "Upload a PDF file to automatically parse and create chunks"
        )

    def test_context_form_validates_pdf_upload(self):
        """Test that the ContextForm properly validates PDF uploads."""
        from rag.admin import ContextForm

        # Test with valid PDF file
        pdf_content = b"%PDF-1.4\nMock PDF content"
        uploaded_file = SimpleUploadedFile(
            "test.pdf", pdf_content, content_type="application/pdf"
        )

        with patch("rag.validators.FileValidator.validate_file") as mock_validate:
            mock_result = Mock()
            mock_result.is_valid = True
            mock_result.file_type = "pdf"
            mock_validate.return_value = mock_result

            form_data = {
                "name": "Test PDF Context",
                "description": "Test description",
                "context_type": "PDF",
                "chunk_count": 0,
                "processing_status": "PENDING",
            }
            file_data = MultiValueDict(
                {"uploaded_file": [cast(UploadedFile, uploaded_file)]}
            )

            form = ContextForm(data=form_data, files=file_data)
            self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_context_form_rejects_invalid_pdf_for_pdf_type(self):
        """Test that the ContextForm rejects invalid files for PDF context type."""
        from rag.admin import ContextForm

        # Test with invalid file for PDF context type
        invalid_file = SimpleUploadedFile(
            "test.txt", b"Not a PDF", content_type="text/plain"
        )

        with patch("rag.validators.FileValidator.validate_file") as mock_validate:
            mock_result = Mock()
            mock_result.is_valid = True
            mock_result.file_type = "text"  # Wrong type for PDF context
            mock_validate.return_value = mock_result

            form_data = {
                "name": "Test PDF Context",
                "description": "Test description",
                "context_type": "PDF",
                "chunk_count": 0,
                "processing_status": "PENDING",
            }
            file_data = MultiValueDict(
                {"uploaded_file": [cast(UploadedFile, invalid_file)]}
            )

            form = ContextForm(data=form_data, files=file_data)
            self.assertFalse(form.is_valid())
            self.assertIn("Only PDF files are supported", str(form.errors))
