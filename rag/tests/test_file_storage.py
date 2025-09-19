from io import BytesIO
from unittest.mock import MagicMock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from rag.storage import MinIOStorage
from rag.validators import FileValidator


class MinIOStorageTest(TestCase):
    def setUp(self):
        self.storage = MinIOStorage()
        self.test_bucket = "test-bucket"
        self.test_file_content = b"Test file content for MinIO upload"
        self.test_file_name = "test_document.pdf"

    def test_minio_storage_initialization(self):
        """Test MinIOStorage initializes with correct configuration."""
        self.assertIsNotNone(self.storage.client)
        self.assertEqual(self.storage.bucket_name, "scholaria-docs")

    @patch("rag.storage.Minio")
    def test_upload_file_success(self, mock_minio_class):
        """Test successful file upload to MinIO."""
        mock_client = MagicMock()
        mock_minio_class.return_value = mock_client

        file_obj = BytesIO(self.test_file_content)

        storage = MinIOStorage()
        result = storage.upload_file(self.test_file_name, file_obj)

        mock_client.put_object.assert_called_once()
        call_args = mock_client.put_object.call_args
        self.assertEqual(call_args[1]["bucket_name"], "scholaria-docs")
        self.assertEqual(call_args[1]["object_name"], self.test_file_name)
        self.assertEqual(call_args[1]["data"], file_obj)
        self.assertEqual(call_args[1]["length"], len(self.test_file_content))

        self.assertEqual(result, self.test_file_name)

    @patch("rag.storage.Minio")
    def test_download_file_success(self, mock_minio_class):
        """Test successful file download from MinIO."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.read.return_value = self.test_file_content
        mock_client.get_object.return_value = mock_response
        mock_minio_class.return_value = mock_client

        storage = MinIOStorage()
        result = storage.download_file(self.test_file_name)

        mock_client.get_object.assert_called_once_with(
            "scholaria-docs", self.test_file_name
        )
        self.assertEqual(result, self.test_file_content)

    @patch("rag.storage.Minio")
    def test_file_exists_true(self, mock_minio_class):
        """Test file_exists returns True when file exists."""
        mock_client = MagicMock()
        mock_client.stat_object.return_value = MagicMock()
        mock_minio_class.return_value = mock_client

        storage = MinIOStorage()
        result = storage.file_exists(self.test_file_name)

        mock_client.stat_object.assert_called_once_with(
            "scholaria-docs", self.test_file_name
        )
        self.assertTrue(result)

    @patch("rag.storage.Minio")
    def test_file_exists_false(self, mock_minio_class):
        """Test file_exists returns False when file does not exist."""
        from minio.error import S3Error

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_client.stat_object.side_effect = S3Error(
            "NoSuchKey",
            "The specified key does not exist",
            "bucket",
            "request-id",
            "host-id",
            mock_response,
        )
        mock_minio_class.return_value = mock_client

        storage = MinIOStorage()
        result = storage.file_exists(self.test_file_name)

        self.assertFalse(result)

    @patch("rag.storage.Minio")
    def test_delete_file_success(self, mock_minio_class):
        """Test successful file deletion from MinIO."""
        mock_client = MagicMock()
        mock_minio_class.return_value = mock_client

        storage = MinIOStorage()
        result = storage.delete_file(self.test_file_name)

        mock_client.remove_object.assert_called_once_with(
            "scholaria-docs", self.test_file_name
        )
        self.assertTrue(result)

    @patch("rag.storage.Minio")
    def test_delete_file_not_found(self, mock_minio_class):
        """Test deleting a non-existent file returns False."""
        from minio.error import S3Error

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_client.remove_object.side_effect = S3Error(
            "NoSuchKey",
            "The specified key does not exist",
            "bucket",
            "request-id",
            "host-id",
            mock_response,
        )
        mock_minio_class.return_value = mock_client

        storage = MinIOStorage()
        result = storage.delete_file(self.test_file_name)

        self.assertFalse(result)

    @patch("rag.storage.Minio")
    def test_get_file_url(self, mock_minio_class):
        """Test generating presigned URL for file access."""
        mock_client = MagicMock()
        expected_url = (
            "https://localhost:9000/scholaria-docs/test_document.pdf?presigned=params"
        )
        mock_client.presigned_get_object.return_value = expected_url
        mock_minio_class.return_value = mock_client

        storage = MinIOStorage()
        result = storage.get_file_url(self.test_file_name, expires=3600)

        mock_client.presigned_get_object.assert_called_once_with(
            "scholaria-docs", self.test_file_name, expires=3600
        )
        self.assertEqual(result, expected_url)

    @patch("rag.storage.Minio")
    def test_upload_from_django_file(self, mock_minio_class):
        """Test uploading Django UploadedFile to MinIO."""
        mock_client = MagicMock()
        mock_minio_class.return_value = mock_client

        uploaded_file = SimpleUploadedFile(
            name="upload_test.pdf",
            content=self.test_file_content,
            content_type="application/pdf",
        )

        storage = MinIOStorage()
        result = storage.upload_django_file(uploaded_file)

        mock_client.put_object.assert_called_once()
        call_args = mock_client.put_object.call_args
        self.assertEqual(call_args[1]["bucket_name"], "scholaria-docs")
        self.assertEqual(call_args[1]["object_name"], "upload_test.pdf")
        self.assertEqual(call_args[1]["content_type"], "application/pdf")

        self.assertEqual(result, "upload_test.pdf")

    @patch("rag.storage.Minio")
    def test_list_files_in_bucket(self, mock_minio_class):
        """Test listing files in MinIO bucket."""
        mock_client = MagicMock()
        mock_objects = [
            MagicMock(object_name="file1.pdf"),
            MagicMock(object_name="file2.txt"),
            MagicMock(object_name="file3.md"),
        ]
        mock_client.list_objects.return_value = mock_objects
        mock_minio_class.return_value = mock_client

        storage = MinIOStorage()
        result = storage.list_files(prefix="")

        mock_client.list_objects.assert_called_once_with("scholaria-docs", prefix="")
        expected_files = ["file1.pdf", "file2.txt", "file3.md"]
        self.assertEqual(result, expected_files)

    @patch("rag.storage.Minio")
    def test_ensure_bucket_exists(self, mock_minio_class):
        """Test bucket creation if it doesn't exist."""
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = False
        mock_minio_class.return_value = mock_client

        storage = MinIOStorage()
        storage.ensure_bucket_exists()

        mock_client.bucket_exists.assert_called_once_with("scholaria-docs")
        mock_client.make_bucket.assert_called_once_with("scholaria-docs")

    @patch("rag.storage.Minio")
    def test_bucket_already_exists(self, mock_minio_class):
        """Test no bucket creation when bucket already exists."""
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_minio_class.return_value = mock_client

        storage = MinIOStorage()
        storage.ensure_bucket_exists()

        mock_client.bucket_exists.assert_called_once_with("scholaria-docs")
        mock_client.make_bucket.assert_not_called()


class FileValidatorTest(TestCase):
    def setUp(self):
        self.validator = FileValidator()

    def test_valid_pdf_file(self):
        """Test validation of a valid PDF file."""
        pdf_content = b"%PDF-1.4\nTest PDF content"
        uploaded_file = SimpleUploadedFile(
            name="test.pdf", content=pdf_content, content_type="application/pdf"
        )

        result = self.validator.validate_file(uploaded_file)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.file_type, "pdf")
        self.assertEqual(result.errors or [], [])

    def test_valid_markdown_file(self):
        """Test validation of a valid Markdown file."""
        md_content = b"# Test Markdown\n\nThis is a test markdown file."
        uploaded_file = SimpleUploadedFile(
            name="test.md", content=md_content, content_type="text/markdown"
        )

        result = self.validator.validate_file(uploaded_file)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.file_type, "markdown")
        self.assertEqual(result.errors or [], [])

    def test_valid_text_file(self):
        """Test validation of a valid text file."""
        txt_content = b"This is a plain text file for testing."
        uploaded_file = SimpleUploadedFile(
            name="test.txt", content=txt_content, content_type="text/plain"
        )

        result = self.validator.validate_file(uploaded_file)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.file_type, "text")
        self.assertEqual(result.errors or [], [])

    def test_unsupported_file_type(self):
        """Test rejection of unsupported file types."""
        exe_content = b"MZ\x90\x00"  # PE header for executable
        uploaded_file = SimpleUploadedFile(
            name="malware.exe",
            content=exe_content,
            content_type="application/octet-stream",
        )

        result = self.validator.validate_file(uploaded_file)
        self.assertFalse(result.is_valid)
        errors = result.errors or []
        self.assertIn("Unsupported file type", errors[0])

    def test_file_too_large(self):
        """Test rejection of files that are too large."""
        # Create a file larger than max size (10MB)
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        uploaded_file = SimpleUploadedFile(
            name="large.pdf", content=large_content, content_type="application/pdf"
        )

        result = self.validator.validate_file(uploaded_file)
        self.assertFalse(result.is_valid)
        errors = result.errors or []
        self.assertIn("File size exceeds maximum", errors[0])

    def test_empty_file(self):
        """Test rejection of empty files."""
        uploaded_file = SimpleUploadedFile(
            name="empty.pdf", content=b"", content_type="application/pdf"
        )

        result = self.validator.validate_file(uploaded_file)
        self.assertFalse(result.is_valid)
        errors = result.errors or []
        self.assertIn("File is empty", errors[0])

    def test_malicious_filename(self):
        """Test detection of potentially malicious filenames."""
        malicious_files = [
            "../../../etc/passwd",
            "file.pdf.exe",
            "normal.pdf\x00hidden.exe",
            "con.pdf",  # Windows reserved name
            "script.pdf.js",
        ]

        for filename in malicious_files:
            with self.subTest(filename=filename):
                # Test the validation method directly since Django normalizes filenames
                errors = self.validator._validate_filename(filename)
                self.assertTrue(
                    len(errors) > 0,
                    f"No errors found for malicious filename: {filename}",
                )
                self.assertTrue(
                    any(
                        "filename" in error.lower() or "invalid" in error.lower()
                        for error in errors
                    )
                )

    def test_pdf_magic_bytes_validation(self):
        """Test that PDF files are validated by magic bytes, not just extension."""
        fake_pdf_content = b"This is not a real PDF file"
        uploaded_file = SimpleUploadedFile(
            name="fake.pdf", content=fake_pdf_content, content_type="application/pdf"
        )

        result = self.validator.validate_file(uploaded_file)
        self.assertFalse(result.is_valid)
        errors = result.errors or []
        self.assertIn("Invalid PDF file", errors[0])

    def test_virus_scan_simulation(self):
        """Test virus scanning simulation (mock)."""
        # Simulate a file that would be flagged by antivirus
        suspicious_content = (
            b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
        )
        uploaded_file = SimpleUploadedFile(
            name="eicar.txt", content=suspicious_content, content_type="text/plain"
        )

        result = self.validator.validate_file(uploaded_file)
        self.assertFalse(result.is_valid)
        errors = result.errors or []
        self.assertIn("Security scan failed", errors[0])

    def test_filename_sanitization(self):
        """Test that filenames are properly sanitized."""
        test_cases = [
            ("My Document.pdf", "my_document.pdf"),
            ("file with spaces.txt", "file_with_spaces.txt"),
            ("special!@#$%.md", "special_.md"),
            ("unicode_文档.pdf", "unicode_.pdf"),
            ("UPPERCASE.PDF", "uppercase.pdf"),
        ]

        for input_name, expected_name in test_cases:
            with self.subTest(input_name=input_name):
                sanitized = self.validator.sanitize_filename(input_name)
                self.assertEqual(sanitized, expected_name)

    def test_content_type_validation(self):
        """Test content type validation against file extension."""
        # Mismatched content type and extension
        uploaded_file = SimpleUploadedFile(
            name="document.pdf",
            content=b"# This is markdown content",
            content_type="text/markdown",  # Wrong content type for .pdf
        )

        result = self.validator.validate_file(uploaded_file)
        self.assertFalse(result.is_valid)
        errors = result.errors or []
        self.assertIn("Content type mismatch", errors[0])

    def test_validate_file_content_safety(self):
        """Test validation of file content for safety."""
        # Test content with potential script injection
        dangerous_content = b"<script>alert('xss')</script>\n# Markdown Header"
        uploaded_file = SimpleUploadedFile(
            name="test.md", content=dangerous_content, content_type="text/markdown"
        )

        result = self.validator.validate_file(uploaded_file)
        self.assertFalse(result.is_valid)
        errors = result.errors or []
        self.assertIn("Potentially dangerous content", errors[0])
