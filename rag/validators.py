from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from django.core.files.uploadedfile import UploadedFile


class FileTypeConfig(TypedDict):
    extensions: list[str]
    content_types: list[str]
    magic_bytes: list[bytes]


@dataclass
class ValidationResult:
    """Result of file validation."""

    is_valid: bool
    file_type: str = ""
    errors: list[str] | None = None

    def __post_init__(self) -> None:
        if self.errors is None:
            self.errors = []


class FileValidator:
    """File validation service for security and safety checks."""

    # Maximum file size: 10MB
    MAX_FILE_SIZE = 10 * 1024 * 1024

    # Supported file types and their magic bytes
    SUPPORTED_TYPES: dict[str, FileTypeConfig] = {
        "pdf": {
            "extensions": [".pdf"],
            "content_types": ["application/pdf"],
            "magic_bytes": [b"%PDF-"],
        },
        "markdown": {
            "extensions": [".md", ".markdown"],
            "content_types": ["text/markdown", "text/x-markdown"],
            "magic_bytes": [],  # No specific magic bytes for markdown
        },
        "text": {
            "extensions": [".txt"],
            "content_types": ["text/plain"],
            "magic_bytes": [],  # No specific magic bytes for plain text
        },
    }

    # Windows reserved filenames
    WINDOWS_RESERVED = {
        "con",
        "prn",
        "aux",
        "nul",
        "com1",
        "com2",
        "com3",
        "com4",
        "com5",
        "com6",
        "com7",
        "com8",
        "com9",
        "lpt1",
        "lpt2",
        "lpt3",
        "lpt4",
        "lpt5",
        "lpt6",
        "lpt7",
        "lpt8",
        "lpt9",
    }

    # EICAR test virus signature for security testing
    EICAR_SIGNATURE = (
        b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    )

    def validate_file(self, uploaded_file: UploadedFile) -> ValidationResult:
        """Validate an uploaded file for security and safety.

        Args:
            uploaded_file: Django UploadedFile instance

        Returns:
            ValidationResult with validation status and errors
        """
        errors = []

        # Check file size
        if uploaded_file.size == 0:
            errors.append("File is empty")
            return ValidationResult(is_valid=False, errors=errors)

        if uploaded_file.size and uploaded_file.size > self.MAX_FILE_SIZE:
            errors.append(
                f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE // (1024*1024)}MB"
            )
            return ValidationResult(is_valid=False, errors=errors)

        # Validate filename
        filename_errors: list[str] = []
        if uploaded_file.name:
            filename_errors = self._validate_filename(uploaded_file.name)
            errors.extend(filename_errors)
        else:
            errors.append("Filename is required")
            return ValidationResult(is_valid=False, errors=errors)

        # If filename validation failed, return early
        if filename_errors:
            return ValidationResult(is_valid=False, errors=errors)

        # Determine file type
        file_type = self._determine_file_type(uploaded_file)
        if not file_type:
            errors.append("Unsupported file type")
            return ValidationResult(is_valid=False, errors=errors)

        # Validate content type matches extension
        content_type_errors = self._validate_content_type(uploaded_file, file_type)
        errors.extend(content_type_errors)

        # Validate file content
        content_errors = self._validate_file_content(uploaded_file, file_type)
        errors.extend(content_errors)

        # Security scan
        security_errors = self._security_scan(uploaded_file)
        errors.extend(security_errors)

        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, file_type=file_type, errors=errors)

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize a filename for safe storage.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove null bytes
        filename = filename.replace("\x00", "")

        # Replace spaces with underscores
        filename = filename.replace(" ", "_")

        # Replace special characters with underscores, but preserve dots, hyphens, and underscores
        filename = re.sub(r"[^\w\-_.]", "_", filename)

        # Remove non-ASCII characters
        filename = re.sub(r"[^\x00-\x7F]", "_", filename)

        # Collapse multiple underscores
        filename = re.sub(r"_{2,}", "_", filename)

        # Convert to lowercase
        filename = filename.lower()

        # Remove leading/trailing underscores
        filename = filename.strip("_")

        return filename

    def _validate_filename(self, filename: str) -> list[str]:
        """Validate filename for security issues."""
        errors = []

        if not filename:
            errors.append("Filename is required")
            return errors

        # Check for path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            errors.append("Invalid filename: path traversal detected")

        # Check for null bytes
        if "\x00" in filename:
            errors.append("Invalid filename: null byte detected")

        # Check for Windows reserved names
        basename = os.path.splitext(filename.lower())[0]
        if basename in self.WINDOWS_RESERVED:
            errors.append("Invalid filename: reserved system name")

        # Check for double extensions (potential disguised executables)
        parts = filename.lower().split(".")
        if len(parts) > 2:
            executable_exts = [
                "exe",
                "bat",
                "cmd",
                "com",
                "pif",
                "scr",
                "vbs",
                "js",
                "jar",
            ]
            # Check if the final extension is executable
            if parts[-1] in executable_exts:
                errors.append("Invalid filename: executable file type not allowed")
            # Also check if any middle part is an executable extension
            for part in parts[1:-1]:  # Skip first (name) and last (final extension)
                if part in executable_exts:
                    errors.append("Invalid filename: potential disguised executable")
                    break

        return errors

    def _determine_file_type(self, uploaded_file: UploadedFile) -> str:
        """Determine file type based on extension and content type."""
        if not uploaded_file.name:
            return ""

        filename = uploaded_file.name.lower()
        content_type = uploaded_file.content_type

        for file_type, config in self.SUPPORTED_TYPES.items():
            # Check extension
            extensions = config["extensions"]
            if any(filename.endswith(ext) for ext in extensions):
                return file_type

            # Check content type as fallback
            content_types = config["content_types"]
            if content_type in content_types:
                return file_type

        return ""

    def _validate_content_type(
        self, uploaded_file: UploadedFile, file_type: str
    ) -> list[str]:
        """Validate that content type matches the determined file type."""
        errors: list[str] = []

        if file_type not in self.SUPPORTED_TYPES:
            return errors

        config = self.SUPPORTED_TYPES[file_type]
        expected_content_types = config["content_types"]
        if (
            uploaded_file.content_type
            and uploaded_file.content_type not in expected_content_types
        ):
            # For .txt files with .md extension, allow text/plain
            if file_type == "markdown" and uploaded_file.content_type == "text/plain":
                return errors

            errors.append(
                f"Content type mismatch: expected {expected_content_types}, got {uploaded_file.content_type}"
            )

        return errors

    def _validate_file_content(
        self, uploaded_file: UploadedFile, file_type: str
    ) -> list[str]:
        """Validate file content based on magic bytes and content analysis."""
        errors: list[str] = []

        # Read first few bytes for magic byte validation
        uploaded_file.seek(0)
        header = uploaded_file.read(1024)  # Read first 1KB
        uploaded_file.seek(0)  # Reset position

        # Validate magic bytes for PDF files
        if file_type == "pdf":
            config = self.SUPPORTED_TYPES["pdf"]
            magic_bytes_list = config["magic_bytes"]
            if not any(header.startswith(magic) for magic in magic_bytes_list):
                errors.append("Invalid PDF file: missing PDF header")

        # Check for potentially dangerous content in text files
        if file_type in ["markdown", "text"]:
            try:
                content_str = header.decode("utf-8", errors="ignore")
                # Check for script tags or other dangerous patterns
                dangerous_patterns = [
                    r"<script[^>]*>",
                    r"javascript:",
                    r"vbscript:",
                    r"onclick\s*=",
                    r"onerror\s*=",
                    r"onload\s*=",
                ]

                for pattern in dangerous_patterns:
                    if re.search(pattern, content_str, re.IGNORECASE):
                        errors.append("Potentially dangerous content detected in file")
                        break

            except UnicodeDecodeError:
                errors.append("File contains invalid text encoding")

        return errors

    def _security_scan(self, uploaded_file: UploadedFile) -> list[str]:
        """Perform basic security scanning."""
        errors = []

        # Read file content for scanning
        uploaded_file.seek(0)
        content = uploaded_file.read()
        uploaded_file.seek(0)  # Reset position

        # Check for EICAR test virus signature
        if self.EICAR_SIGNATURE in content:
            errors.append("Security scan failed: test virus signature detected")

        # Additional security checks could be added here
        # such as integration with real antivirus scanners

        return errors
