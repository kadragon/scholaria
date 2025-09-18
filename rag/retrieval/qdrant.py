from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.conf import settings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from rag.models import ContextItem

if TYPE_CHECKING:
    pass


class QdrantService:
    """Service for vector storage and similarity search using Qdrant."""

    def __init__(self) -> None:
        # In a real environment, these would come from settings
        self.client = QdrantClient(
            host=getattr(settings, "QDRANT_HOST", "localhost"),
            port=getattr(settings, "QDRANT_PORT", 6333),
        )
        self.collection_name = "context_items"
        self.vector_size = 1536  # OpenAI text-embedding-3-small dimension

    def create_collection(self) -> bool:
        """
        Create the collection for storing context item embeddings.

        Returns:
            True if successful
        """
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_size, distance=Distance.COSINE
            ),
        )
        return True

    def store_embedding(
        self,
        context_item_id: int,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Store an embedding for a context item.

        Args:
            context_item_id: ID of the ContextItem
            embedding: Vector embedding to store
            metadata: Additional metadata to store with the vector

        Returns:
            Operation ID from Qdrant

        Raises:
            ValueError: If context item doesn't exist or embedding is empty
        """
        if not embedding:
            raise ValueError("Embedding cannot be empty")

        # Verify context item exists
        try:
            context_item = ContextItem.objects.get(id=context_item_id)
        except ContextItem.DoesNotExist:
            raise ValueError(
                f"ContextItem with ID {context_item_id} does not exist"
            ) from None

        # Prepare payload with metadata
        payload = {
            "context_item_id": context_item_id,
            "title": context_item.title,
            "content": context_item.content,
            "context_id": context_item.context_id,
            "context_type": context_item.context.context_type,
        }

        if metadata:
            payload.update(metadata)

        # Create point and upsert
        point = PointStruct(id=context_item_id, vector=embedding, payload=payload)

        response = self.client.upsert(
            collection_name=self.collection_name, points=[point]
        )

        return str(response.operation_id)

    def search_similar(
        self, query_embedding: list[float], topic_ids: list[int], limit: int = 5
    ) -> list[dict[str, Any]]:
        """
        Search for similar context items by embedding.

        Args:
            query_embedding: Query vector
            topic_ids: List of topic IDs to filter by
            limit: Maximum number of results to return

        Returns:
            List of search results with scores and metadata

        Raises:
            ValueError: If query_embedding is empty or topic_ids is empty
        """
        if not query_embedding:
            raise ValueError("Query embedding cannot be empty")

        if not topic_ids:
            raise ValueError("Topic IDs cannot be empty")

        # Build filter for topics
        # For now, we'll implement a simple filter
        # In a real implementation, we'd need to join with Topic-Context relationships
        query_filter = {
            "must": [
                {
                    "key": "context_id",
                    "match": {"any": topic_ids},  # Simplified - will need refinement
                }
            ]
        }

        # Perform search
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=query_filter,
            limit=limit,
        )

        # Format results
        results = []
        for scored_point in search_results:
            if scored_point.payload:
                result = {
                    "context_item_id": scored_point.payload["context_item_id"],
                    "score": scored_point.score,
                    "title": scored_point.payload.get("title", ""),
                    "content": scored_point.payload.get("content", ""),
                    "context_id": scored_point.payload.get("context_id"),
                    "context_type": scored_point.payload.get("context_type"),
                }
                results.append(result)

        return results
