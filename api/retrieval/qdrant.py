from __future__ import annotations

from typing import TYPE_CHECKING, Any

import qdrant_client
from django.conf import settings
from django.core.cache import cache
from qdrant_client.models import Distance, PointStruct, VectorParams

from api.models import ContextItem, Topic

if TYPE_CHECKING:
    pass


class QdrantService:
    """Service for vector storage and similarity search using Qdrant."""

    def __init__(self) -> None:
        # Keep original client creation for compatibility
        self.client = qdrant_client.QdrantClient(
            host=getattr(settings, "QDRANT_HOST", "localhost"),
            port=getattr(settings, "QDRANT_PORT", 6333),
        )
        self.collection_name = getattr(
            settings, "QDRANT_COLLECTION_NAME", "context_items"
        )
        self.vector_size = getattr(
            settings, "OPENAI_EMBEDDING_DIM", 1536
        )  # OpenAI text-embedding-3-small dimension

    def create_collection(self) -> bool:
        """
        Create the collection for storing context item embeddings.
        If collection already exists, returns True without error.

        Returns:
            True if successful or already exists
        """
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size, distance=Distance.COSINE
                ),
            )
            return True
        except Exception as e:
            # Check if the error is about collection already existing
            if "already exists" in str(e):
                return True
            raise

    def reset_collection(self) -> bool:
        """Recreate the collection with the configured vector size."""
        self.client.recreate_collection(
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
            context_item = ContextItem.objects.select_related("context").get(
                id=context_item_id
            )
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

    def _get_context_ids_for_topics(self, topic_ids: list[int]) -> list[int]:
        """
        Get context IDs for given topics with caching optimization.

        Args:
            topic_ids: List of topic IDs

        Returns:
            List of context IDs
        """
        # Create cache key from sorted topic IDs for consistent caching
        cache_key = f"topic_contexts:{'_'.join(map(str, sorted(topic_ids)))}"

        # Try to get from cache first (5 minute TTL)
        context_ids = cache.get(cache_key)
        if context_ids is not None:
            return context_ids

        # Query database with optimized select_related/prefetch_related
        context_ids = list(
            Topic.objects.filter(id__in=topic_ids)
            .values_list("contexts__id", flat=True)
            .distinct()
        )

        # Filter out None values (topics without contexts)
        context_ids = [cid for cid in context_ids if cid is not None]

        # Cache the result for 5 minutes
        cache.set(cache_key, context_ids, 300)

        return context_ids

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

        # Get context IDs with caching optimization
        context_ids = self._get_context_ids_for_topics(topic_ids)

        if not context_ids:
            return []

        # Build optimized filter for Qdrant
        query_filter = {
            "must": [
                {
                    "key": "context_id",
                    "match": {"any": context_ids},
                }
            ]
        }

        # Perform vector search
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=query_filter,
            limit=limit,
        )

        # Format results efficiently
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
