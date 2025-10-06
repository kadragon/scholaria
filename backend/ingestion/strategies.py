from __future__ import annotations

from abc import ABC, abstractmethod


class BaseIngestionStrategy(ABC):
    """Abstract base class for document ingestion strategies."""

    @abstractmethod
    def parse(self, file_path: str) -> str:
        """
        Parse a document file and extract text content.

        Args:
            file_path: Path to the file to parse

        Returns:
            Extracted text content as string

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        pass

    @abstractmethod
    def chunk(self, text: str) -> list[str]:
        """
        Split text into chunks.

        Args:
            text: Text to be chunked

        Returns:
            List of text chunks
        """
        pass


class PDFIngestionStrategy(BaseIngestionStrategy):
    """Ingestion strategy for PDF documents."""

    def __init__(self, chunk_size: int = 1000, overlap: int = 150) -> None:
        """
        Initialize PDF ingestion strategy.

        Args:
            chunk_size: Maximum size of each chunk in characters
            overlap: Number of overlapping characters between chunks
        """
        from backend.ingestion.chunkers import PDFChunker
        from backend.ingestion.parsers import PDFParser

        self.parser = PDFParser()
        self.chunker = PDFChunker(chunk_size=chunk_size, overlap=overlap)

    def parse(self, file_path: str) -> str:
        """Parse PDF file and extract text content."""
        return self.parser.parse_file(file_path)

    def chunk(self, text: str) -> list[str]:
        """Chunk PDF text using PDF-aware chunking."""
        return self.chunker.chunk_text(text)


class MarkdownIngestionStrategy(BaseIngestionStrategy):
    """Ingestion strategy for Markdown documents."""

    def __init__(self, chunk_size: int = 1200, overlap: int = 200) -> None:
        """
        Initialize Markdown ingestion strategy.

        Args:
            chunk_size: Maximum size of each chunk in characters
            overlap: Number of overlapping characters between chunks
        """
        from backend.ingestion.chunkers import MarkdownChunker
        from backend.ingestion.parsers import MarkdownParser

        self.parser = MarkdownParser()
        self.chunker = MarkdownChunker(chunk_size=chunk_size, overlap=overlap)

    def parse(self, file_path: str) -> str:
        """Parse Markdown file and return content."""
        return self.parser.parse_file(file_path)

    def chunk(self, text: str) -> list[str]:
        """Chunk Markdown text respecting structure."""
        return self.chunker.chunk_text(text)


class FAQIngestionStrategy(BaseIngestionStrategy):
    """Ingestion strategy for FAQ documents."""

    def __init__(self, chunk_size: int = 800, overlap: int = 100) -> None:
        """
        Initialize FAQ ingestion strategy.

        Args:
            chunk_size: Maximum size of each chunk in characters
            overlap: Number of overlapping characters between chunks
        """
        from backend.ingestion.chunkers import FAQChunker
        from backend.ingestion.parsers import FAQParser

        self.parser = FAQParser()
        self.chunker = FAQChunker(chunk_size=chunk_size, overlap=overlap)

    def parse(self, file_path: str) -> str:
        """Parse FAQ file and return formatted content."""
        return self.parser.parse_file(file_path)

    def chunk(self, text: str) -> list[str]:
        """Chunk FAQ text keeping Q&A pairs together."""
        return self.chunker.chunk_text(text)


class WebScraperIngestionStrategy(BaseIngestionStrategy):
    """Ingestion strategy for web-scraped documents."""

    def __init__(self, chunk_size: int = 1000, overlap: int = 150) -> None:
        """
        Initialize WebScraper ingestion strategy.

        Args:
            chunk_size: Maximum size of each chunk in characters
            overlap: Number of overlapping characters between chunks
        """
        from backend.ingestion.chunkers import WebScraperChunker
        from backend.ingestion.parsers import WebScraperParser

        self.parser = WebScraperParser()
        self.chunker = WebScraperChunker(chunk_size=chunk_size, overlap=overlap)

    def parse(self, url: str) -> str:
        """Parse web URL and extract text content using Puppeteer."""
        return self.parser.parse_url(url)

    def chunk(self, text: str) -> list[str]:
        """Chunk web-scraped text using web-aware chunking."""
        return self.chunker.chunk_text(text)


def get_ingestion_strategy(context_type: str) -> BaseIngestionStrategy:
    """
    Factory function to get the appropriate ingestion strategy.

    Args:
        context_type: Type of context (PDF, MARKDOWN, FAQ, WEBSCRAPER)

    Returns:
        Appropriate ingestion strategy instance

    Raises:
        ValueError: If context type is not supported
    """
    strategy_map = {
        "PDF": PDFIngestionStrategy(),
        "MARKDOWN": MarkdownIngestionStrategy(),
        "FAQ": FAQIngestionStrategy(),
        "WEBSCRAPER": WebScraperIngestionStrategy(),
    }

    strategy = strategy_map.get(context_type)
    if strategy is None:
        raise ValueError(f"Unsupported context type: {context_type}")

    return strategy
