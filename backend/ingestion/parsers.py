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

        document = getattr(converted, "document", None) if converted else None
        text_content = document.export_to_text() if document else ""
        return text_content or ""


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

        return content.strip()


class WebScraperParser:
    """Parser for web pages using Puppeteer service."""

    def __init__(self, puppeteer_url: str | None = None) -> None:
        """
        Initialize WebScraperParser.

        Args:
            puppeteer_url: URL of Puppeteer service (defaults to config)
        """
        if puppeteer_url is None:
            from backend.config import settings

            puppeteer_url = settings.PUPPETEER_URL

        self.puppeteer_url = puppeteer_url

    def parse_url(self, url: str) -> str:
        """
        Parse a web page URL and extract text content using Puppeteer.

        Args:
            url: URL to scrape

        Returns:
            Extracted text content as string

        Raises:
            ValueError: If URL is invalid or scraping fails
            TimeoutError: If Puppeteer service times out
        """
        import requests

        if not url or not url.startswith("http"):
            raise ValueError(f"Invalid URL: {url}")

        try:
            response = requests.post(
                f"{self.puppeteer_url}/scrape",
                json={"url": url},
                timeout=190,
            )

            if response.status_code != 200:
                error_msg = response.json().get("error", "Unknown error")
                raise ValueError(f"Puppeteer scraping failed: {error_msg}")

            data = response.json()
            text: str = str(data.get("text", ""))

            if not text:
                raise ValueError("No text extracted from URL")

            return text

        except requests.Timeout as e:
            raise TimeoutError(f"Puppeteer service timeout: {url}") from e
        except requests.RequestException as e:
            raise ValueError(f"Failed to connect to Puppeteer service: {e}") from e
