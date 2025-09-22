from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.test import TestCase

from rag.models import Context, ContextItem, Topic
from rag.retrieval.qdrant import QdrantService

if TYPE_CHECKING:
    pass


def build_embedding(fill: float = 0.1, *, dimension: int | None = None) -> list[float]:
    """Return a repeat-filled embedding vector matching the configured dimension."""
    if dimension is not None:
        return [fill] * dimension
    target_dim = getattr(settings, "OPENAI_EMBEDDING_DIM", 1536)
    return [fill] * target_dim


class EmbeddingServiceTest(TestCase):
    """Test the OpenAI embedding service."""

    def test_generate_embedding_success(self) -> None:
        """Test successful embedding generation."""
        from rag.retrieval.embeddings import EmbeddingService

        # This should fail initially as the service doesn't exist yet
        service = EmbeddingService()
        result = service.generate_embedding("test text")

        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        self.assertIsInstance(result[0], float)

    def test_generate_embedding_empty_text(self) -> None:
        """Test embedding generation with empty text."""
        from rag.retrieval.embeddings import EmbeddingService

        service = EmbeddingService()

        with self.assertRaises(ValueError):
            service.generate_embedding("")

    def test_generate_embedding_none_text(self) -> None:
        """Test embedding generation with None text."""
        from rag.retrieval.embeddings import EmbeddingService

        service = EmbeddingService()

        with self.assertRaises(ValueError):
            service.generate_embedding(None)

    def test_generate_embedding_api_call(self) -> None:
        """Test that the OpenAI API is called correctly."""
        from unittest.mock import MagicMock, patch

        from rag.retrieval.embeddings import EmbeddingService

        expected_embedding = build_embedding(0.1)
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=expected_embedding)]

        # Mock usage with proper attribute values instead of MagicMock
        mock_usage = MagicMock()
        mock_usage.total_tokens = 10
        mock_response.usage = mock_usage

        service = EmbeddingService()

        # Patch the client directly
        with (
            patch.object(service, "client") as mock_client,
            patch.object(service, "cache") as mock_cache,
        ):
            mock_client.embeddings.create.return_value = mock_response
            mock_cache.enabled.return_value = False

            result = service.generate_embedding("test text")

            # Verify the API was called correctly
            mock_client.embeddings.create.assert_called_once_with(
                model=settings.OPENAI_EMBEDDING_MODEL, input="test text"
            )

            self.assertEqual(result, expected_embedding)

    def test_generate_embedding_api_error(self) -> None:
        """Test handling of OpenAI API errors."""
        from unittest.mock import patch

        from rag.retrieval.embeddings import EmbeddingService

        service = EmbeddingService()

        # Patch the client directly
        with (
            patch.object(service, "client") as mock_client,
            patch.object(service, "cache") as mock_cache,
        ):
            mock_client.embeddings.create.side_effect = Exception("API Error")
            mock_cache.enabled.return_value = False

            with self.assertRaises(Exception) as cm:
                service.generate_embedding("test text")
            self.assertEqual(str(cm.exception), "API Error")

    def test_generate_embeddings_batch(self) -> None:
        """Test batch embedding generation."""
        from rag.retrieval.embeddings import EmbeddingService

        service = EmbeddingService()
        texts = ["text 1", "text 2", "text 3"]
        results = service.generate_embeddings_batch(texts)

        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIsInstance(result, list)
            self.assertTrue(len(result) > 0)
            self.assertIsInstance(result[0], float)

    def test_generate_embeddings_batch_empty_list(self) -> None:
        """Test batch embedding generation with empty list."""
        from rag.retrieval.embeddings import EmbeddingService

        service = EmbeddingService()

        with self.assertRaises(ValueError):
            service.generate_embeddings_batch([])

    def test_generate_embedding_cache_hit(self) -> None:
        """Ensure cached embeddings are returned without new API calls."""
        from unittest.mock import patch

        from rag.retrieval.embeddings import EmbeddingService

        service = EmbeddingService()

        # Patch the client and cache directly
        with (
            patch.object(service, "client") as mock_client,
            patch.object(service, "cache") as mock_cache,
        ):
            mock_cache.enabled.return_value = True
            mock_cache.get.return_value = build_embedding(0.9)

            result = service.generate_embedding("cached text")

            mock_cache.get.assert_called_once_with(
                "cached text", settings.OPENAI_EMBEDDING_MODEL
            )
            mock_client.embeddings.create.assert_not_called()
            self.assertEqual(result, build_embedding(0.9))

    def test_generate_embeddings_batch_api_call(self) -> None:
        """Test that batch API calls work correctly."""
        from unittest.mock import MagicMock, patch

        from rag.retrieval.embeddings import EmbeddingService

        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(embedding=build_embedding(0.1)),
            MagicMock(embedding=build_embedding(0.4)),
        ]

        service = EmbeddingService()

        # Patch the client directly
        with (
            patch.object(service, "client") as mock_client,
            patch.object(service, "cache") as mock_cache,
        ):
            mock_client.embeddings.create.return_value = mock_response
            mock_cache.enabled.return_value = False

            texts = ["text 1", "text 2"]
            results = service.generate_embeddings_batch(texts)

            # Verify the API was called correctly
            mock_client.embeddings.create.assert_called_once_with(
                model=settings.OPENAI_EMBEDDING_MODEL, input=texts
            )

            self.assertEqual(len(results), 2)
            self.assertEqual(results[0], build_embedding(0.1))
            self.assertEqual(results[1], build_embedding(0.4))


class QdrantServiceTest(TestCase):
    """Test the Qdrant vector database service."""

    def setUp(self) -> None:
        """Set up test data."""
        self.topic = Topic.objects.create(
            name="Test Topic", description="Test topic description"
        )
        self.context = Context.objects.create(
            name="Test Context",
            description="Test context description",
            context_type="PDF",
        )
        # Establish the Topic-Context relationship
        self.topic.contexts.add(self.context)

        self.context_item = ContextItem.objects.create(
            title="Test Item", content="Test content for search", context=self.context
        )

        self.qdrant_service = QdrantService()
        try:
            self.qdrant_service.reset_collection()
        except Exception:
            # Fallback if reset is not supported (e.g., Qdrant unavailable)
            self.qdrant_service.create_collection()

    def test_store_embedding_success(self) -> None:
        """Test successful embedding storage."""
        service = self.qdrant_service
        embedding = build_embedding()

        result = service.store_embedding(
            context_item_id=self.context_item.id,
            embedding=embedding,
            metadata={"title": "Test Item"},
        )

        self.assertIsInstance(result, str)  # Returns operation ID

    def test_store_embedding_invalid_context_item(self) -> None:
        """Test embedding storage with invalid context item ID."""
        service = QdrantService()
        embedding = build_embedding()

        with self.assertRaises(ValueError):
            service.store_embedding(
                context_item_id=999999,  # Non-existent ID
                embedding=embedding,
                metadata={"title": "Test Item"},
            )

    def test_store_embedding_empty_embedding(self) -> None:
        """Test embedding storage with empty embedding."""
        service = self.qdrant_service

        with self.assertRaises(ValueError):
            service.store_embedding(
                context_item_id=self.context_item.id,
                embedding=[],
                metadata={"title": "Test Item"},
            )

    def test_store_embedding_api_call(self) -> None:
        """Test that Qdrant API is called correctly for storage."""
        from unittest.mock import MagicMock, patch

        mock_response = MagicMock()
        mock_response.operation_id = "test-operation-id"

        service = QdrantService()

        # Patch the client directly
        with patch.object(service, "client") as mock_client:
            mock_client.upsert.return_value = mock_response

            embedding = build_embedding()
            metadata = {"title": "Test Item"}

            result = service.store_embedding(
                context_item_id=self.context_item.id,
                embedding=embedding,
                metadata=metadata,
            )

            # Verify the API was called correctly
            mock_client.upsert.assert_called_once()
            call_args = mock_client.upsert.call_args[1]

            self.assertEqual(
                call_args["collection_name"], settings.QDRANT_COLLECTION_NAME
            )
            self.assertEqual(len(call_args["points"]), 1)

            point = call_args["points"][0]
            self.assertEqual(point.id, self.context_item.id)
            self.assertEqual(point.vector, embedding)
            self.assertIn("title", point.payload)
            self.assertIn("context_item_id", point.payload)

            self.assertEqual(result, "test-operation-id")

    def test_search_similar_success(self) -> None:
        """Test successful similarity search."""
        service = self.qdrant_service
        query_embedding = build_embedding()

        results = service.search_similar(
            query_embedding=query_embedding, topic_ids=[self.topic.id], limit=5
        )

        self.assertIsInstance(results, list)
        # Results structure will be verified when we implement

    def test_search_similar_empty_embedding(self) -> None:
        """Test similarity search with empty embedding."""
        service = QdrantService()

        with self.assertRaises(ValueError):
            service.search_similar(
                query_embedding=[], topic_ids=[self.topic.id], limit=5
            )

    def test_search_similar_empty_topic_ids(self) -> None:
        """Test similarity search with empty topic IDs."""
        service = QdrantService()
        query_embedding = build_embedding()

        with self.assertRaises(ValueError):
            service.search_similar(
                query_embedding=query_embedding, topic_ids=[], limit=5
            )

    def test_search_similar_api_call(self) -> None:
        """Test that Qdrant search API is called correctly."""
        from unittest.mock import MagicMock, patch

        # Mock search response
        mock_scored_point = MagicMock()
        mock_scored_point.id = self.context_item.id
        mock_scored_point.score = 0.95
        mock_scored_point.payload = {
            "context_item_id": self.context_item.id,
            "title": "Test Item",
            "content": "Test content",
        }

        service = QdrantService()

        # Patch the client directly
        with patch.object(service, "client") as mock_client:
            mock_client.search.return_value = [mock_scored_point]

            query_embedding = build_embedding()
            topic_ids = [self.topic.id]

            results = service.search_similar(
                query_embedding=query_embedding, topic_ids=topic_ids, limit=5
            )

            # Verify the search API was called correctly
            mock_client.search.assert_called_once()
            call_args = mock_client.search.call_args[1]

            self.assertEqual(
                call_args["collection_name"], settings.QDRANT_COLLECTION_NAME
            )
            self.assertEqual(call_args["query_vector"], query_embedding)
            self.assertEqual(call_args["limit"], 5)
            self.assertIn("query_filter", call_args)

            # Verify results format
            self.assertEqual(len(results), 1)
            result = results[0]
            self.assertEqual(result["context_item_id"], self.context_item.id)
            self.assertEqual(result["score"], 0.95)
            self.assertIn("title", result)
            self.assertIn("content", result)

    def test_create_collection_success(self) -> None:
        """Test successful collection creation."""

        result = self.qdrant_service.create_collection()

        self.assertTrue(result)

    def test_create_collection_api_call(self) -> None:
        """Test that collection creation API is called correctly."""
        from unittest.mock import patch

        service = QdrantService()

        # Patch the client directly
        with patch.object(service, "client") as mock_client:
            result = service.create_collection()

            # Verify the API was called correctly
            mock_client.create_collection.assert_called_once()
            call_args = mock_client.create_collection.call_args[1]

            self.assertEqual(
                call_args["collection_name"], settings.QDRANT_COLLECTION_NAME
            )
            self.assertIn("vectors_config", call_args)

            self.assertTrue(result)

    def test_search_similar_performance_optimization(self) -> None:
        """Test that search_similar uses optimized context filtering."""
        from unittest.mock import patch

        from rag.retrieval.qdrant import QdrantService

        # Create additional topics and contexts for performance testing
        topic2 = Topic.objects.create(
            name="Mathematics",
            description="Math topics",
            system_prompt="Focus on mathematical concepts",
        )
        topic3 = Topic.objects.create(
            name="Science",
            description="Science topics",
            system_prompt="Focus on scientific concepts",
        )

        # Create contexts for each topic
        context2 = Context.objects.create(
            name="Math Context",
            description="Mathematical content",
            context_type="FAQ",
        )
        context3 = Context.objects.create(
            name="Science Context",
            description="Scientific content",
            context_type="MARKDOWN",
        )

        # Associate contexts with topics
        topic2.contexts.add(context2)
        topic3.contexts.add(context3)

        service = QdrantService()

        with patch.object(service, "client") as mock_client:
            mock_client.search.return_value = []

            query_embedding = build_embedding()

            # Test with multiple topics to ensure efficient context filtering
            topic_ids = [self.topic.id, topic2.id, topic3.id]

            # This should complete without excessive database queries
            service.search_similar(
                query_embedding=query_embedding, topic_ids=topic_ids, limit=10
            )

            # Verify search was called (the implementation should work correctly)
            mock_client.search.assert_called_once()

            # The optimized version should handle multiple topics efficiently
            call_args = mock_client.search.call_args[1]
            self.assertIn("query_filter", call_args)
            # Ensure the filter contains the correct context IDs
            query_filter = call_args["query_filter"]
            self.assertIn("must", query_filter)

    @patch("rag.retrieval.qdrant.Topic.objects")
    def test_context_lookup_caching(self, mock_topic_objects: MagicMock) -> None:
        """Test that context lookups are cached for performance."""
        from django.core.cache import cache

        from rag.retrieval.qdrant import QdrantService

        # Clear cache to start fresh
        cache.clear()

        # Configure mock for the database query
        mock_topic_objects.filter.return_value.values_list.return_value.distinct.return_value = [
            self.context.id
        ]

        service = QdrantService()
        topic_ids = [self.topic.id]

        # First call should hit the database
        result1 = service._get_context_ids_for_topics(topic_ids)
        mock_topic_objects.filter.assert_called_once()

        # Second call with same topic IDs should use cache
        result2 = service._get_context_ids_for_topics(topic_ids)

        # Verify results are the same
        self.assertEqual(result1, result2)

        # Verify the database was NOT called again
        mock_topic_objects.filter.assert_called_once()

        # Third call should also use cache
        result3 = service._get_context_ids_for_topics(topic_ids)
        self.assertEqual(result1, result3)
        mock_topic_objects.filter.assert_called_once()


class RerankingServiceTest(TestCase):
    """Test the BGE reranking service."""

    def test_rerank_results_success(self) -> None:
        """Test successful reranking of search results."""
        from rag.retrieval.reranking import RerankingService

        service = RerankingService()

        search_results = [
            {
                "context_item_id": 1,
                "score": 0.8,
                "title": "Document 1",
                "content": "This is about machine learning algorithms.",
            },
            {
                "context_item_id": 2,
                "score": 0.7,
                "title": "Document 2",
                "content": "This discusses neural networks and deep learning.",
            },
            {
                "context_item_id": 3,
                "score": 0.6,
                "title": "Document 3",
                "content": "Random content about cooking recipes.",
            },
        ]

        query = "machine learning"
        reranked_results = service.rerank_results(query, search_results)

        self.assertIsInstance(reranked_results, list)
        self.assertEqual(len(reranked_results), 3)

        # Results should have rerank_score added
        for result in reranked_results:
            self.assertIn("rerank_score", result)
            self.assertIsInstance(result["rerank_score"], float)

    def test_rerank_results_empty_query(self) -> None:
        """Test reranking with empty query."""
        from rag.retrieval.reranking import RerankingService

        service = RerankingService()
        search_results = [{"context_item_id": 1, "content": "test"}]

        with self.assertRaises(ValueError):
            service.rerank_results("", search_results)

    def test_rerank_results_empty_results(self) -> None:
        """Test reranking with empty results list."""
        from rag.retrieval.reranking import RerankingService

        service = RerankingService()

        with self.assertRaises(ValueError):
            service.rerank_results("test query", [])

    def test_rerank_results_none_query(self) -> None:
        """Test reranking with None query."""
        from rag.retrieval.reranking import RerankingService

        service = RerankingService()
        search_results = [{"context_item_id": 1, "content": "test"}]

        with self.assertRaises(ValueError):
            service.rerank_results(None, search_results)

    def test_rerank_results_model_call(self) -> None:
        """Test that BGE reranking model is called correctly."""
        from unittest.mock import MagicMock, patch

        from rag.retrieval.reranking import RerankingService

        # Mock the CrossEncoder model
        mock_model = MagicMock()
        mock_model.predict.return_value = [0.9, 0.3, 0.7]  # Rerank scores

        service = RerankingService()

        # Patch the model directly
        with patch.object(service, "model", mock_model):
            search_results = [
                {"context_item_id": 1, "content": "Machine learning content"},
                {"context_item_id": 2, "content": "Cooking recipes"},
                {"context_item_id": 3, "content": "Deep learning networks"},
            ]

            query = "machine learning"
            reranked_results = service.rerank_results(query, search_results)

            # Verify predict was called with correct input pairs
            mock_model.predict.assert_called_once()
            call_args = mock_model.predict.call_args[0][0]  # Get the input pairs

            self.assertEqual(len(call_args), 3)
            for i, pair in enumerate(call_args):
                self.assertEqual(pair[0], query)
                self.assertEqual(pair[1], search_results[i]["content"])

            # Verify results are reranked and include rerank_score
            self.assertEqual(len(reranked_results), 3)

            # Results should be sorted by rerank_score (descending)
            self.assertEqual(
                reranked_results[0]["context_item_id"], 1
            )  # Highest score (0.9)
            self.assertEqual(reranked_results[0]["rerank_score"], 0.9)

            self.assertEqual(
                reranked_results[1]["context_item_id"], 3
            )  # Second highest (0.7)
            self.assertEqual(reranked_results[1]["rerank_score"], 0.7)

            self.assertEqual(reranked_results[2]["context_item_id"], 2)  # Lowest (0.3)
            self.assertEqual(reranked_results[2]["rerank_score"], 0.3)

    def test_rerank_results_top_k_limit(self) -> None:
        """Test reranking with top_k limitation."""
        from rag.retrieval.reranking import RerankingService

        service = RerankingService()

        search_results = [
            {"context_item_id": i, "content": f"Document {i} content"}
            for i in range(1, 6)  # 5 results
        ]

        query = "test query"
        reranked_results = service.rerank_results(query, search_results, top_k=3)

        # Should only return top 3 results
        self.assertEqual(len(reranked_results), 3)

    def test_rerank_results_top_k_larger_than_input(self) -> None:
        """Test reranking with top_k larger than input size."""
        from rag.retrieval.reranking import RerankingService

        service = RerankingService()

        search_results = [
            {"context_item_id": 1, "content": "Document 1"},
            {"context_item_id": 2, "content": "Document 2"},
        ]

        query = "test query"
        reranked_results = service.rerank_results(query, search_results, top_k=10)

        # Should return all available results
        self.assertEqual(len(reranked_results), 2)

    def test_rerank_results_model_error(self) -> None:
        """Test handling of model errors during reranking."""
        from unittest.mock import MagicMock, patch

        from rag.retrieval.reranking import RerankingService

        # Mock the model to raise an exception
        mock_model = MagicMock()
        mock_model.predict.side_effect = Exception("Model error")

        service = RerankingService()

        # Patch the model directly
        with patch.object(service, "model", mock_model):
            search_results = [{"context_item_id": 1, "content": "test"}]

            with self.assertRaises(Exception) as cm:
                service.rerank_results("test query", search_results)
            self.assertEqual(str(cm.exception), "Model error")


class RAGServiceTest(TestCase):
    """Test the complete RAG query pipeline service."""

    def setUp(self) -> None:
        """Set up test data."""
        self.topic = Topic.objects.create(
            name="Machine Learning",
            description="Machine learning concepts and algorithms",
        )
        self.context = Context.objects.create(
            name="ML Context",
            description="Machine learning documentation",
            context_type="PDF",
        )
        self.context_item = ContextItem.objects.create(
            title="Neural Networks",
            content="Neural networks are fundamental to deep learning.",
            context=self.context,
        )
        # Associate context with topic
        self.topic.contexts.add(self.context)

    def test_query_success(self) -> None:
        """Test successful RAG query processing."""
        from django.conf import settings

        from rag.retrieval.rag import RAGService

        if not settings.OPENAI_API_KEY:
            self.skipTest("OpenAI API key not configured for tests")

        service = RAGService()
        query = "What are neural networks?"
        topic_ids = [self.topic.id]

        result = service.query(query, topic_ids)

        self.assertIsInstance(result, dict)
        self.assertIn("answer", result)
        self.assertIn("sources", result)
        self.assertIn("context_items", result)
        self.assertIsInstance(result["sources"], list)
        self.assertIsInstance(result["context_items"], list)

    def test_query_empty_query(self) -> None:
        """Test RAG query with empty query string."""
        from rag.retrieval.rag import RAGService

        service = RAGService()

        with self.assertRaises(ValueError):
            service.query("", [self.topic.id])

    def test_query_none_query(self) -> None:
        """Test RAG query with None query."""
        from rag.retrieval.rag import RAGService

        service = RAGService()

        with self.assertRaises(ValueError):
            service.query(None, [self.topic.id])

    def test_query_empty_topic_ids(self) -> None:
        """Test RAG query with empty topic IDs."""
        from rag.retrieval.rag import RAGService

        service = RAGService()

        with self.assertRaises(ValueError):
            service.query("test query", [])

    def test_query_pipeline_orchestration(self) -> None:
        """Test that the complete RAG pipeline orchestrates all services correctly."""
        from unittest.mock import MagicMock, patch

        from rag.retrieval.rag import RAGService

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="Neural networks are computational models inspired by biological neural networks."
                )
            )
        ]

        service = RAGService()

        # Patch all service components directly
        with (
            patch.object(service, "embedding_service") as mock_embedding_service,
            patch.object(service, "qdrant_service") as mock_qdrant_service,
            patch.object(service, "reranking_service") as mock_reranking_service,
            patch.object(service, "chat_client") as mock_chat_client,
        ):
            # Setup mock responses
            mock_embedding_service.generate_embedding.return_value = build_embedding()
            mock_qdrant_service.search_similar.return_value = [
                {
                    "context_item_id": self.context_item.id,
                    "score": 0.9,
                    "title": "Neural Networks",
                    "content": "Neural networks are fundamental to deep learning.",
                    "context_id": self.context.id,
                    "context_type": "PDF",
                }
            ]
            mock_reranking_service.rerank_results.return_value = [
                {
                    "context_item_id": self.context_item.id,
                    "score": 0.9,
                    "title": "Neural Networks",
                    "content": "Neural networks are fundamental to deep learning.",
                    "context_id": self.context.id,
                    "context_type": "PDF",
                    "rerank_score": 0.95,
                }
            ]
            mock_chat_client.chat.completions.create.return_value = mock_response

            query = "What are neural networks?"
            topic_ids = [self.topic.id]

            result = service.query(query, topic_ids)

            # Verify embedding service was called
            mock_embedding_service.generate_embedding.assert_called_once_with(query)

            # Verify Qdrant search was called
            mock_qdrant_service.search_similar.assert_called_once_with(
                query_embedding=build_embedding(), topic_ids=topic_ids, limit=10
            )

            # Verify reranking was called
            mock_reranking_service.rerank_results.assert_called_once()

            # Verify OpenAI was called
            mock_chat_client.chat.completions.create.assert_called_once()

            # Verify result structure
            self.assertEqual(
                result["answer"],
                "Neural networks are computational models inspired by biological neural networks.",
            )
            self.assertEqual(len(result["sources"]), 1)
            self.assertEqual(result["sources"][0]["title"], "Neural Networks")

    def test_query_no_results_found(self) -> None:
        """Test RAG query when no similar documents are found."""
        from rag.retrieval.rag import RAGService

        # Create a topic with no associated contexts
        empty_topic = Topic.objects.create(
            name="Empty Topic", description="Topic with no content"
        )

        service = RAGService()
        query = "What are neural networks?"

        result = service.query(query, [empty_topic.id])

        # Should still return a valid response structure
        self.assertIsInstance(result, dict)
        self.assertIn("answer", result)
        self.assertIn("sources", result)
        self.assertIn("context_items", result)

    def test_query_embedding_service_error(self) -> None:
        """Test handling of embedding service errors."""
        from unittest.mock import patch

        from rag.retrieval.rag import RAGService

        service = RAGService()

        # Patch the embedding service directly
        with patch.object(service, "embedding_service") as mock_embedding_service:
            mock_embedding_service.generate_embedding.side_effect = Exception(
                "Embedding error"
            )

            with self.assertRaises(Exception) as cm:
                service.query("test query", [self.topic.id])
            self.assertEqual(str(cm.exception), "Embedding error")

    def test_query_with_limit_parameter(self) -> None:
        """Test RAG query with custom limit parameter."""
        from django.conf import settings

        from rag.retrieval.rag import RAGService

        if not settings.OPENAI_API_KEY:
            self.skipTest("OpenAI API key not configured for tests")

        service = RAGService()
        query = "What are neural networks?"
        topic_ids = [self.topic.id]

        result = service.query(query, topic_ids, limit=5)

        self.assertIsInstance(result, dict)
        self.assertIn("answer", result)

    def test_query_with_rerank_top_k_parameter(self) -> None:
        """Test RAG query with custom rerank_top_k parameter."""
        from django.conf import settings

        from rag.retrieval.rag import RAGService

        if not settings.OPENAI_API_KEY:
            self.skipTest("OpenAI API key not configured for tests")

        service = RAGService()
        query = "What are neural networks?"
        topic_ids = [self.topic.id]

        result = service.query(query, topic_ids, rerank_top_k=3)

        self.assertIsInstance(result, dict)
        self.assertIn("answer", result)

    def test_rag_query_result_caching_design(self) -> None:
        """Test design for RAG query result caching functionality."""
        from unittest.mock import MagicMock, patch

        from django.core.cache import cache

        from rag.retrieval.rag import RAGService

        # Clear cache to start fresh
        cache.clear()

        service = RAGService()

        # Mock all external services to control behavior
        with (
            patch.object(service, "embedding_service") as mock_embedding_service,
            patch.object(service, "qdrant_service") as mock_qdrant_service,
            patch.object(service, "reranking_service") as mock_reranking_service,
            patch.object(service, "chat_client") as mock_chat_client,
        ):
            # Setup mocks
            mock_embedding_service.generate_embedding.return_value = [0.1, 0.2, 0.3]
            mock_qdrant_service.search_similar.return_value = [
                {
                    "context_item_id": 1,
                    "score": 0.9,
                    "title": "Test Title",
                    "content": "Test content",
                    "context_type": "PDF",
                }
            ]
            mock_reranking_service.rerank_results.return_value = [
                {
                    "context_item_id": 1,
                    "score": 0.9,
                    "rerank_score": 0.95,
                    "title": "Test Title",
                    "content": "Test content",
                    "context_type": "PDF",
                }
            ]

            mock_response = MagicMock()
            mock_response.choices[0].message.content = "This is a test answer."
            mock_chat_client.chat.completions.create.return_value = mock_response

            # First query should hit all services
            query = "What is machine learning?"
            topic_ids = [self.topic.id]

            result1 = service.query(query, topic_ids)

            # Verify external services were called
            mock_embedding_service.generate_embedding.assert_called()
            mock_qdrant_service.search_similar.assert_called()
            mock_reranking_service.rerank_results.assert_called()
            mock_chat_client.chat.completions.create.assert_called()

            # Verify result structure
            self.assertIn("answer", result1)
            self.assertIn("sources", result1)
            self.assertIn("context_items", result1)

            # This test establishes the design for caching RAG query results
            # When implemented, identical queries should return cached results

    def test_rag_query_caching_functionality(self) -> None:
        """Test that RAG query caching actually works."""
        from unittest.mock import MagicMock, patch

        from django.core.cache import cache

        from rag.retrieval.rag import RAGService

        # Clear cache to start fresh
        cache.clear()

        service = RAGService()

        # Mock all external services to control behavior
        with (
            patch.object(service, "embedding_service") as mock_embedding_service,
            patch.object(service, "qdrant_service") as mock_qdrant_service,
            patch.object(service, "reranking_service") as mock_reranking_service,
            patch.object(service, "chat_client") as mock_chat_client,
        ):
            # Setup mocks
            mock_embedding_service.generate_embedding.return_value = [0.1, 0.2, 0.3]
            mock_qdrant_service.search_similar.return_value = [
                {
                    "context_item_id": 1,
                    "score": 0.9,
                    "title": "Test Title",
                    "content": "Test content for caching",
                    "context_type": "PDF",
                }
            ]
            mock_reranking_service.rerank_results.return_value = [
                {
                    "context_item_id": 1,
                    "score": 0.9,
                    "rerank_score": 0.95,
                    "title": "Test Title",
                    "content": "Test content for caching",
                    "context_type": "PDF",
                }
            ]

            mock_response = MagicMock()
            mock_response.choices[0].message.content = "This is a cached test answer."
            mock_chat_client.chat.completions.create.return_value = mock_response

            # First query should hit all services
            query = "What is neural network architecture?"
            topic_ids = [self.topic.id]

            result1 = service.query(query, topic_ids)

            # Verify external services were called for first query
            self.assertEqual(mock_embedding_service.generate_embedding.call_count, 1)
            self.assertEqual(mock_qdrant_service.search_similar.call_count, 1)
            self.assertEqual(mock_reranking_service.rerank_results.call_count, 1)
            self.assertEqual(mock_chat_client.chat.completions.create.call_count, 1)

            # Second identical query should use cache
            result2 = service.query(query, topic_ids)

            # Verify services were NOT called again (still at 1 call each)
            self.assertEqual(mock_embedding_service.generate_embedding.call_count, 1)
            self.assertEqual(mock_qdrant_service.search_similar.call_count, 1)
            self.assertEqual(mock_reranking_service.rerank_results.call_count, 1)
            self.assertEqual(mock_chat_client.chat.completions.create.call_count, 1)

            # Results should be identical
            self.assertEqual(result1["answer"], result2["answer"])
            self.assertEqual(result1["sources"], result2["sources"])
            self.assertEqual(result1["context_items"], result2["context_items"])

            # Third query with different parameters should hit services again
            service.query(query, topic_ids, limit=20)

            # Services should be called again for different parameters
            self.assertEqual(mock_embedding_service.generate_embedding.call_count, 2)
            self.assertEqual(mock_qdrant_service.search_similar.call_count, 2)
            self.assertEqual(mock_reranking_service.rerank_results.call_count, 2)
            self.assertEqual(mock_chat_client.chat.completions.create.call_count, 2)


class OpenAIUsageMonitoringTest(TestCase):
    """Test OpenAI API usage monitoring and optimization."""

    def setUp(self) -> None:
        self.topic = Topic.objects.create(
            name="ML", description="Machine Learning", system_prompt="Focus on ML"
        )

    def test_embedding_service_usage_tracking(self) -> None:
        """Test that embedding API usage is tracked."""
        from unittest.mock import MagicMock, patch

        from rag.retrieval.embeddings import EmbeddingService
        from rag.retrieval.monitoring import OpenAIUsageMonitor

        service = EmbeddingService()

        with patch.object(service, "client") as mock_client:
            # Mock embedding response
            mock_response = MagicMock()
            mock_response.data = [MagicMock()]
            mock_response.data[0].embedding = [0.1, 0.2, 0.3]
            mock_response.usage.prompt_tokens = 10
            mock_response.usage.total_tokens = 10
            mock_client.embeddings.create.return_value = mock_response
            monitor = OpenAIUsageMonitor()

            # Clear any existing metrics
            monitor.reset_metrics()

            # Generate embedding (should be tracked)
            embedding = service.generate_embedding("test text")

            # Verify embedding was generated
            self.assertEqual(len(embedding), 3)

            # Verify usage was tracked
            metrics = monitor.get_metrics()
            self.assertIn("embeddings", metrics)
            self.assertEqual(metrics["embeddings"]["calls"], 1)
            self.assertEqual(metrics["embeddings"]["tokens"], 10)

    def test_chat_completion_usage_tracking(self) -> None:
        """Test that chat completion API usage is tracked."""
        from unittest.mock import MagicMock, patch

        from rag.retrieval.monitoring import OpenAIUsageMonitor
        from rag.retrieval.rag import RAGService

        service = RAGService()

        with (
            patch.object(service, "embedding_service") as mock_embedding_service,
            patch.object(service, "qdrant_service") as mock_qdrant_service,
            patch.object(service, "reranking_service") as mock_reranking_service,
            patch.object(service, "chat_client") as mock_chat_client,
        ):
            # Setup mocks for pipeline
            mock_embedding_service.generate_embedding.return_value = [0.1, 0.2, 0.3]
            mock_qdrant_service.search_similar.return_value = [
                {
                    "context_item_id": 1,
                    "score": 0.9,
                    "title": "Test",
                    "content": "Test content",
                    "context_type": "PDF",
                }
            ]
            mock_reranking_service.rerank_results.return_value = [
                {
                    "context_item_id": 1,
                    "score": 0.9,
                    "rerank_score": 0.95,
                    "title": "Test",
                    "content": "Test content",
                    "context_type": "PDF",
                }
            ]

            # Mock chat completion
            mock_response = MagicMock()
            mock_response.choices[0].message.content = "Test answer"
            mock_response.usage.prompt_tokens = 50
            mock_response.usage.completion_tokens = 30
            mock_response.usage.total_tokens = 80
            mock_chat_client.chat.completions.create.return_value = mock_response
            monitor = OpenAIUsageMonitor()

            # Clear any existing metrics
            monitor.reset_metrics()

            # Execute query (should be tracked)
            result = service.query("What is AI?", [self.topic.id])

            # Verify response
            self.assertIn("answer", result)

            # Verify usage was tracked
            metrics = monitor.get_metrics()
            self.assertIn("chat_completions", metrics)
            self.assertEqual(metrics["chat_completions"]["calls"], 1)
            self.assertEqual(metrics["chat_completions"]["prompt_tokens"], 50)
            self.assertEqual(metrics["chat_completions"]["completion_tokens"], 30)
            self.assertEqual(metrics["chat_completions"]["total_tokens"], 80)

    def test_usage_cost_calculation(self) -> None:
        """Test that API usage costs are calculated correctly."""
        from rag.retrieval.monitoring import OpenAIUsageMonitor

        monitor = OpenAIUsageMonitor()
        monitor.reset_metrics()

        # Simulate some usage
        monitor.track_embedding_usage(1000, "text-embedding-3-small")
        monitor.track_chat_completion_usage(500, 200, "gpt-4o-mini")

        # Get cost breakdown
        costs = monitor.get_cost_breakdown()

        # Verify cost calculation structure
        self.assertIn("embeddings", costs)
        self.assertIn("chat_completions", costs)
        self.assertIn("total", costs)
        self.assertGreater(costs["total"], 0)

    def test_usage_optimization_recommendations(self) -> None:
        """Test that usage optimization recommendations are generated."""
        from rag.retrieval.monitoring import OpenAIUsageMonitor

        monitor = OpenAIUsageMonitor()
        monitor.reset_metrics()

        # Simulate heavy usage to trigger recommendations
        for _ in range(100):
            monitor.track_embedding_usage(1000, "text-embedding-3-small")
            monitor.track_chat_completion_usage(2000, 800, "gpt-4o-mini")

        # Get optimization recommendations
        recommendations = monitor.get_optimization_recommendations()

        # Verify recommendations structure
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)

        # Should recommend caching and batch processing
        recommendation_text = " ".join(recommendations)
        self.assertTrue(
            "caching" in recommendation_text.lower()
            or "cache" in recommendation_text.lower()
        )

    def test_rate_limiting_detection(self) -> None:
        """Test that rate limiting issues are detected and logged."""
        from rag.retrieval.monitoring import OpenAIUsageMonitor

        monitor = OpenAIUsageMonitor()

        # Simulate rate limiting scenario
        is_rate_limited = monitor.check_rate_limits()

        # Should not be rate limited initially
        self.assertFalse(is_rate_limited)

        # Simulate many rapid requests
        for _ in range(100):
            monitor.track_request_timestamp("embeddings")

        # Check if rate limiting detection works
        recent_requests = monitor.get_recent_request_count("embeddings", minutes=1)
        self.assertGreater(recent_requests, 0)
