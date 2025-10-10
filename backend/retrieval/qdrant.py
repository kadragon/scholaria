from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

import qdrant_client
from qdrant_client.models import Distance, PointStruct, VectorParams
from sqlalchemy import select

from backend.config import settings
from backend.models import ContextItem
from backend.models.associations import topic_context_association
from backend.models.base import SessionLocal
from backend.observability import get_tracer

if TYPE_CHECKING:
    pass

tracer = get_tracer(__name__)


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
        self._context_cache: dict[str, tuple[float, list[int]]] = {}
        self._context_cache_ttl = 300  # seconds

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
        with SessionLocal() as session:
            context_item = session.get(ContextItem, context_item_id)
            if context_item is None:
                raise ValueError(
                    f"ContextItem with ID {context_item_id} does not exist"
                )

            context = context_item.context
            payload = {
                "context_item_id": context_item_id,
                "title": context_item.title,
                "content": context_item.content,
                "context_id": context_item.context_id,
                "context_type": context.context_type if context else "",
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
        now = time.time()

        cached = self._context_cache.get(cache_key)
        if cached and now - cached[0] < self._context_cache_ttl:
            return cached[1]

        stmt = (
            select(topic_context_association.c.context_id)
            .where(topic_context_association.c.topic_id.in_(topic_ids))
            .distinct()
        )

        with SessionLocal() as session:
            context_ids = [
                ctx_id for ctx_id in session.execute(stmt).scalars() if ctx_id
            ]

        self._context_cache[cache_key] = (now, context_ids)

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
        with tracer.start_as_current_span("rag.vector_search") as span:
            if not query_embedding:
                raise ValueError("Query embedding cannot be empty")

            if not topic_ids:
                raise ValueError("Topic IDs cannot be empty")

            span.set_attribute("topic_ids.count", len(topic_ids))
            span.set_attribute("search.limit", limit)

            # Get context IDs with caching optimization
            context_ids = self._get_context_ids_for_topics(topic_ids)

            if not context_ids:
                span.set_attribute("results.count", 0)
                return []

            span.set_attribute("context_ids.count", len(context_ids))

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

            span.set_attribute("results.count", len(results))
            if results:
                span.set_attribute("score.max", max(r["score"] for r in results))
                span.set_attribute("score.min", min(r["score"] for r in results))

            return results
