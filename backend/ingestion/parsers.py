from __future__ import annotations

import re
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
    """Parser for web pages using Playwright."""

    def parse_url(self, url: str) -> str:
        """
        Parse a web page URL and extract text content using Playwright.

        Args:
            url: URL to scrape

        Returns:
            Extracted text content as string

        Raises:
            ValueError: If URL is invalid or scraping fails
            TimeoutError: If browser times out
        """
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright

        if not url or not url.startswith("http"):
            raise ValueError(f"Invalid URL: {url}")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                try:
                    page = browser.new_page()

                    page.goto(url, wait_until="networkidle", timeout=180000)

                    has_iframe = page.locator("iframe#innerWrap").count() > 0
                    if has_iframe:
                        iframe_src = page.evaluate(
                            """() => {
                            const iframe = document.querySelector('iframe#innerWrap');
                            return iframe ? iframe.src : null;
                        }"""
                        )
                        if iframe_src:
                            page.goto(
                                iframe_src, wait_until="networkidle", timeout=180000
                            )

                    page.evaluate(
                        """async () => {
                        let prev = 0, sameCount = 0, totalHeight = 0;
                        while (true) {
                            window.scrollBy(0, 300);
                            await new Promise(r => setTimeout(r, 200));
                            let sh = document.body.scrollHeight;
                            totalHeight += 300;
                            if (sh === prev) {
                                sameCount++;
                            } else {
                                sameCount = 0;
                                prev = sh;
                            }
                            if (sameCount >= 5) break;
                            if (totalHeight > 1000000) break;
                        }
                        await new Promise(r => setTimeout(r, 2000));
                    }"""
                    )

                    selectors = [".synap-page", ".page", ".document-page"]
                    texts = []

                    for selector in selectors:
                        nodes = page.locator(selector).all()
                        if nodes:
                            texts = [
                                node.inner_text().strip()
                                for node in nodes
                                if node.inner_text().strip()
                            ]
                            if texts:
                                break

                    if not texts:
                        body_text = page.evaluate("() => document.body.innerText")
                        texts = [body_text] if body_text else []

                    final_text = "\n\n".join(texts)
                    sanitized_text = re.sub(r"<[^>]*>", "", final_text)

                    if not sanitized_text:
                        raise ValueError("No text extracted from URL")

                    return sanitized_text

                finally:
                    browser.close()

        except PlaywrightTimeoutError as e:
            raise TimeoutError(f"Browser timeout: {url}") from e
        except Exception as e:
            raise ValueError(f"Failed to scrape URL: {e}") from e
