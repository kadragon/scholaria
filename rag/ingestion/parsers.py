from __future__ import annotations

from pathlib import Path
from typing import Any, cast

DocumentConverter: Any | None

try:
    from docling.document_converter import (
        DocumentConverter as _DoclingDocumentConverter,
    )
except ImportError:  # pragma: no cover - fallback handled in runtime logic
    DocumentConverter = None
else:
    DocumentConverter = _DoclingDocumentConverter


class PDFParser:
    """Parser for PDF documents using Docling."""

    def parse_file(self, file_path: str) -> str:
        """
        Parse a PDF file and extract text content.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text content as string

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if DocumentConverter is None:
            raise ImportError(
                "Docling dependency is required for PDF parsing. Install 'docling'."
            )

        converter_cls = cast(Any, DocumentConverter)
        converter = converter_cls()
        converted = converter.convert(file_path)

        if not converted:
            return ""

        document = getattr(converted, "document", None)
        if document is None:
            return ""

        text_content = document.export_to_text()

        if not text_content:
            return ""

        return text_content


class MarkdownParser:
    """Parser for Markdown documents."""

    def parse_file(self, file_path: str) -> str:
        """
        Parse a Markdown file and return content.

        Args:
            file_path: Path to the Markdown file

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        return path.read_text(encoding="utf-8")


class FAQParser:
    """Parser for FAQ documents with question-answer pairs."""

    def parse_file(self, file_path: str) -> str:
        """
        Parse an FAQ file and return formatted content.

        Args:
            file_path: Path to the FAQ file

        Returns:
            FAQ content as formatted string

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = path.read_text(encoding="utf-8")

        if not content.strip():
            return ""

        # Return the content as-is for now, preserving Q&A structure
        # In the future, we could add formatting/parsing logic here
        return content.strip()
