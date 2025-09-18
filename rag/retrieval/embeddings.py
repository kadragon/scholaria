from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from openai import OpenAI

if TYPE_CHECKING:
    pass


class EmbeddingService:
    """Service for generating embeddings using OpenAI API."""

    def __init__(self) -> None:
        self.client = OpenAI()
        self.model = getattr(
            settings, "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
        )

    def generate_embedding(self, text: str | None) -> list[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to generate embedding for

        Returns:
            List of float values representing the embedding

        Raises:
            ValueError: If text is None or empty
        """
        if text is None or not text.strip():
            raise ValueError("Text cannot be None or empty")

        response = self.client.embeddings.create(model=self.model, input=text)

        return response.data[0].embedding

    def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts in a single API call.

        Args:
            texts: List of texts to generate embeddings for

        Returns:
            List of embedding vectors

        Raises:
            ValueError: If texts list is empty
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")

        response = self.client.embeddings.create(model=self.model, input=texts)

        return [item.embedding for item in response.data]
