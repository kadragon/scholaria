from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from unstructured.partition.pdf import partition_pdf

if TYPE_CHECKING:
    pass


class PDFParser:
    """Parser for PDF documents using Unstructured API."""

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

        elements = partition_pdf(filename=file_path)

        if not elements:
            return ""

        # Combine all text elements with newlines
        text_content = "\n".join(element.text for element in elements if element.text)

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
