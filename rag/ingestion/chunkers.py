from __future__ import annotations

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

            # Move start position with overlap
            start += len(chunk_text) - self.overlap

            # Ensure we don't go backwards
            if start <= len("".join(chunks[:-1])) - self.overlap:
                start = len("".join(chunks[:-1])) - self.overlap + 1

        return chunks
