from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class TextChunker:
    """Chunker for splitting text into overlapping chunks."""

    def __init__(self, chunk_size: int = 1000, overlap: int = 200) -> None:
        """
        Initialize the text chunker.

        Args:
            chunk_size: Maximum size of each chunk in characters
            overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> list[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to be chunked

        Returns:
            List of text chunks
        """
        if not text:
            return []

        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            # Calculate end position for current chunk
            end = start + self.chunk_size

            # If this is the last chunk, take all remaining text
            if end >= len(text):
                chunks.append(text[start:])
                break

            # Find a good break point (prefer word boundaries)
            chunk_text = text[start:end]

            # Try to break at a sentence or word boundary
            # Look for sentence endings first
            for break_char in [". ", "! ", "? ", "\n\n"]:
                last_break = chunk_text.rfind(break_char)
                if last_break > self.chunk_size * 0.5:  # Don't break too early
                    chunk_text = text[start : start + last_break + len(break_char)]
                    break
            else:
                # If no sentence break found, try word boundary
                last_space = chunk_text.rfind(" ")
                if last_space > self.chunk_size * 0.5:
                    chunk_text = text[start : start + last_space]

            chunks.append(chunk_text)

            # Move start position with overlap, ensuring we always advance.
            start = max(start + len(chunk_text) - self.overlap, start + 1)

        return chunks


class MarkdownChunker(TextChunker):
    """Optimized chunker for Markdown documents that respects structure."""

    def __init__(self, chunk_size: int = 1200, overlap: int = 200) -> None:
        """
        Initialize the Markdown chunker with optimized defaults.

        Args:
            chunk_size: Maximum size of each chunk in characters
            overlap: Number of overlapping characters between chunks
        """
        super().__init__(chunk_size, overlap)

    def chunk_text(self, text: str) -> list[str]:
        """
        Split Markdown text into chunks respecting document structure.

        Args:
            text: Markdown text to be chunked

        Returns:
            List of text chunks optimized for Markdown structure
        """
        if not text:
            return []

        if len(text) <= self.chunk_size:
            return [text]

        # Try to split by major sections first (# headers)
        section_chunks = self._split_by_sections(text)

        # If section-based splitting produces appropriately sized chunks, use them
        if all(len(chunk) <= self.chunk_size for chunk in section_chunks):
            return section_chunks

        # Otherwise, fall back to standard chunking with Markdown-aware breaks
        return self._markdown_aware_chunking(text)

    def _split_by_sections(self, text: str) -> list[str]:
        """Split text by major Markdown sections (# headers)."""
        # Split by major headers (# but not ## or ###)
        sections = re.split(r"\n(?=# [^#])", text)
        sections = [section.strip() for section in sections if section.strip()]
        return sections

    def _markdown_aware_chunking(self, text: str) -> list[str]:
        """Chunk text with Markdown structure awareness."""
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            if end >= len(text):
                chunks.append(text[start:])
                break

            chunk_text = text[start:end]

            # Look for good break points in order of preference
            break_patterns = [
                r"\n#{1,3} ",  # Headers
                r"\n\n",  # Paragraph breaks
                r"\n- ",  # List items
                r"\n\d+\. ",  # Numbered lists
                r"\n```",  # Code blocks
                r". ",  # Sentences
                r" ",  # Words
            ]

            best_break = None
            for pattern in break_patterns:
                matches = list(re.finditer(pattern, chunk_text))
                if matches:
                    # Find the last match that's not too early
                    for match in reversed(matches):
                        if match.start() > self.chunk_size * 0.4:
                            best_break = start + match.start()
                            break
                    if best_break:
                        break

            if best_break:
                chunks.append(text[start:best_break])
                start = max(best_break - self.overlap, start + 1)
            else:
                # No good break found, use the full chunk
                chunks.append(chunk_text)
                start = max(start + len(chunk_text) - self.overlap, start + 1)

        return chunks


class FAQChunker(TextChunker):
    """Optimized chunker for FAQ documents that keeps Q&A pairs together."""

    def __init__(self, chunk_size: int = 800, overlap: int = 100) -> None:
        """
        Initialize the FAQ chunker with optimized defaults.

        Args:
            chunk_size: Maximum size of each chunk in characters
            overlap: Number of overlapping characters between chunks
        """
        super().__init__(chunk_size, overlap)

    def chunk_text(self, text: str) -> list[str]:
        """
        Split FAQ text into chunks keeping Q&A pairs together.

        Args:
            text: FAQ text to be chunked

        Returns:
            List of text chunks optimized for FAQ structure
        """
        if not text:
            return []

        if len(text) <= self.chunk_size:
            return [text]

        # Split into Q&A pairs first
        qa_pairs = self._extract_qa_pairs(text)

        if qa_pairs:
            return self._chunk_qa_pairs(qa_pairs)
        else:
            # Fall back to standard chunking if no Q&A structure detected
            return super().chunk_text(text)

    def _extract_qa_pairs(self, text: str) -> list[str]:
        """Extract Q&A pairs from FAQ text."""
        # This pattern looks for "Q:" and captures everything until the next "Q:" on a new line or the end of the string.
        qa_pattern = r"Q:.*?(?=\nQ:|\Z)"
        matches = re.findall(qa_pattern, text, re.DOTALL | re.IGNORECASE)
        return [match.strip() for match in matches if match.strip()]

    def _chunk_qa_pairs(self, qa_pairs: list[str]) -> list[str]:
        """Group Q&A pairs into appropriately sized chunks."""
        chunks = []
        current_chunk = ""

        for qa_pair in qa_pairs:
            # If adding this pair would exceed chunk size, finalize current chunk
            if (
                current_chunk
                and len(current_chunk) + len(qa_pair) + 2 > self.chunk_size
            ):
                chunks.append(current_chunk.strip())
                current_chunk = qa_pair
            else:
                # Add to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + qa_pair
                else:
                    current_chunk = qa_pair

        # Add the last chunk if it exists
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks


class PDFChunker(TextChunker):
    """Optimized chunker for PDF documents that handles varied formatting."""

    def __init__(self, chunk_size: int = 1000, overlap: int = 150) -> None:
        """
        Initialize the PDF chunker with optimized defaults.

        Args:
            chunk_size: Maximum size of each chunk in characters
            overlap: Number of overlapping characters between chunks
        """
        super().__init__(chunk_size, overlap)

    def chunk_text(self, text: str) -> list[str]:
        """
        Split PDF text into chunks handling varied document formatting.

        Args:
            text: PDF text to be chunked

        Returns:
            List of text chunks optimized for PDF structure
        """
        if not text:
            return []

        if len(text) <= self.chunk_size:
            return [text]

        # Pre-process text to normalize whitespace and formatting
        normalized_text = self._normalize_pdf_text(text)

        return self._pdf_aware_chunking(normalized_text)

    def _normalize_pdf_text(self, text: str) -> str:
        """Normalize PDF text formatting issues."""
        # Replace multiple whitespace with single spaces
        text = re.sub(r"\s+", " ", text)

        # Restore paragraph breaks (common PDF extraction issue)
        text = re.sub(r"([.!?])\s+([A-Z])", r"\1\n\n\2", text)

        # Restore section headers (words in all caps followed by content)
        text = re.sub(r"\n([A-Z][A-Z\s]+[A-Z])\n", r"\n\n\1\n", text)

        return text.strip()

    def _pdf_aware_chunking(self, text: str) -> list[str]:
        """Chunk text with PDF structure awareness."""
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            if end >= len(text):
                chunks.append(text[start:])
                break

            chunk_text = text[start:end]

            # Look for good break points for PDF content
            break_patterns = [
                r"\n\n[A-Z][A-Z\s]+[A-Z]\n",  # Section headers
                r"\n\n",  # Paragraph breaks
                r"\n•\s",  # Bullet points
                r"\n\d+\.\s",  # Numbered items
                r"[.!?]\s+",  # Sentence endings
                r"\s+",  # Whitespace
            ]

            best_break = None
            for pattern in break_patterns:
                matches = list(re.finditer(pattern, chunk_text))
                if matches:
                    # Find the last match that's not too early
                    for match in reversed(matches):
                        if match.start() > self.chunk_size * 0.3:
                            best_break = start + match.end()
                            break
                    if best_break:
                        break

            if best_break:
                chunks.append(text[start:best_break].strip())
                start = max(best_break - self.overlap, start + 1)
            else:
                # No good break found, use the full chunk
                chunks.append(chunk_text.strip())
                start = max(start + len(chunk_text) - self.overlap, start + 1)

        return [chunk for chunk in chunks if chunk.strip()]


class WebScraperChunker(TextChunker):
    """Optimized chunker for web-scraped documents that handles HTML structure."""

    def __init__(self, chunk_size: int = 1000, overlap: int = 150) -> None:
        """
        Initialize the WebScraper chunker with optimized defaults.

        Args:
            chunk_size: Maximum size of each chunk in characters
            overlap: Number of overlapping characters between chunks
        """
        super().__init__(chunk_size, overlap)

    def chunk_text(self, text: str) -> list[str]:
        """
        Split web-scraped text into chunks respecting document structure.

        Args:
            text: Web-scraped text to be chunked

        Returns:
            List of text chunks optimized for web document structure
        """
        if not text:
            return []

        if len(text) <= self.chunk_size:
            return [text]

        return self._web_aware_chunking(text)

    def _web_aware_chunking(self, text: str) -> list[str]:
        """Chunk text with web document structure awareness."""
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            if end >= len(text):
                chunks.append(text[start:])
                break

            chunk_text = text[start:end]

            break_patterns = [
                r"\n\n+",
                r"\n",
                r"\.\s+",
                r",\s+",
                r"\s+",
            ]

            best_break = None
            for pattern in break_patterns:
                matches = list(re.finditer(pattern, chunk_text))
                if matches:
                    for match in reversed(matches):
                        if match.start() > self.chunk_size * 0.4:
                            best_break = start + match.end()
                            break
                    if best_break:
                        break

            if best_break:
                chunks.append(text[start:best_break].strip())
                start = max(best_break - self.overlap, start + 1)
            else:
                chunks.append(chunk_text.strip())
                start = max(start + len(chunk_text) - self.overlap, start + 1)

        return [chunk for chunk in chunks if chunk.strip()]
