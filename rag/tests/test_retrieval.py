from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from django.test import TestCase

from rag.models import Context, ContextItem, Topic

if TYPE_CHECKING:
    pass


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

    @patch("rag.retrieval.embeddings.OpenAI")
    def test_generate_embedding_api_call(self, mock_openai: MagicMock) -> None:
        """Test that the OpenAI API is called correctly."""
        from rag.retrieval.embeddings import EmbeddingService

        # Mock the OpenAI client and response
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3, 0.4])]
        mock_client.embeddings.create.return_value = mock_response

        service = EmbeddingService()
        result = service.generate_embedding("test text")

        # Verify the API was called correctly
        mock_client.embeddings.create.assert_called_once_with(
            model="text-embedding-3-large", input="test text"
        )

        self.assertEqual(result, [0.1, 0.2, 0.3, 0.4])

    @patch("rag.retrieval.embeddings.OpenAI")
    def test_generate_embedding_api_error(self, mock_openai: MagicMock) -> None:
        """Test handling of OpenAI API errors."""
        from rag.retrieval.embeddings import EmbeddingService

        # Mock the OpenAI client to raise an exception
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.embeddings.create.side_effect = Exception("API Error")

        service = EmbeddingService()

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

    @patch("rag.retrieval.embeddings.OpenAI")
    def test_generate_embeddings_batch_api_call(self, mock_openai: MagicMock) -> None:
        """Test that batch API calls work correctly."""
        from rag.retrieval.embeddings import EmbeddingService

        # Mock the OpenAI client and response
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(embedding=[0.1, 0.2, 0.3, 0.4]),
            MagicMock(embedding=[0.4, 0.5, 0.6, 0.7]),
        ]
        mock_client.embeddings.create.return_value = mock_response

        service = EmbeddingService()
        texts = ["text 1", "text 2"]
        results = service.generate_embeddings_batch(texts)

        # Verify the API was called correctly
        mock_client.embeddings.create.assert_called_once_with(
            model="text-embedding-3-large", input=texts
        )

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], [0.1, 0.2, 0.3, 0.4])
        self.assertEqual(results[1], [0.4, 0.5, 0.6, 0.7])


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

    def test_store_embedding_success(self) -> None:
        """Test successful embedding storage."""
        from rag.retrieval.qdrant import QdrantService

        service = QdrantService()
        embedding = [0.1, 0.2, 0.3, 0.4]

        result = service.store_embedding(
            context_item_id=self.context_item.id,
            embedding=embedding,
            metadata={"title": "Test Item"},
        )

        self.assertIsInstance(result, str)  # Returns operation ID

    def test_store_embedding_invalid_context_item(self) -> None:
        """Test embedding storage with invalid context item ID."""
        from rag.retrieval.qdrant import QdrantService

        service = QdrantService()
        embedding = [0.1, 0.2, 0.3, 0.4]

        with self.assertRaises(ValueError):
            service.store_embedding(
                context_item_id=999999,  # Non-existent ID
                embedding=embedding,
                metadata={"title": "Test Item"},
            )

    def test_store_embedding_empty_embedding(self) -> None:
        """Test embedding storage with empty embedding."""
        from rag.retrieval.qdrant import QdrantService

        service = QdrantService()

        with self.assertRaises(ValueError):
            service.store_embedding(
                context_item_id=self.context_item.id,
                embedding=[],
                metadata={"title": "Test Item"},
            )

    @patch("rag.retrieval.qdrant.QdrantClient")
    def test_store_embedding_api_call(self, mock_qdrant_client: MagicMock) -> None:
        """Test that Qdrant API is called correctly for storage."""
        from rag.retrieval.qdrant import QdrantService

        # Mock the Qdrant client
        mock_client = MagicMock()
        mock_qdrant_client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.operation_id = "test-operation-id"
        mock_client.upsert.return_value = mock_response

        service = QdrantService()
        embedding = [0.1, 0.2, 0.3, 0.4]
        metadata = {"title": "Test Item"}

        result = service.store_embedding(
            context_item_id=self.context_item.id, embedding=embedding, metadata=metadata
        )

        # Verify the API was called correctly
        mock_client.upsert.assert_called_once()
        call_args = mock_client.upsert.call_args[1]

        self.assertEqual(call_args["collection_name"], "context_items")
        self.assertEqual(len(call_args["points"]), 1)

        point = call_args["points"][0]
        self.assertEqual(point.id, self.context_item.id)
        self.assertEqual(point.vector, embedding)
        self.assertIn("title", point.payload)
        self.assertIn("context_item_id", point.payload)

        self.assertEqual(result, "test-operation-id")

    def test_search_similar_success(self) -> None:
        """Test successful similarity search."""
        from rag.retrieval.qdrant import QdrantService

        service = QdrantService()
        query_embedding = [0.1, 0.2, 0.3, 0.4]

        results = service.search_similar(
            query_embedding=query_embedding, topic_ids=[self.topic.id], limit=5
        )

        self.assertIsInstance(results, list)
        # Results structure will be verified when we implement

    def test_search_similar_empty_embedding(self) -> None:
        """Test similarity search with empty embedding."""
        from rag.retrieval.qdrant import QdrantService

        service = QdrantService()

        with self.assertRaises(ValueError):
            service.search_similar(
                query_embedding=[], topic_ids=[self.topic.id], limit=5
            )

    def test_search_similar_empty_topic_ids(self) -> None:
        """Test similarity search with empty topic IDs."""
        from rag.retrieval.qdrant import QdrantService

        service = QdrantService()
        query_embedding = [0.1, 0.2, 0.3, 0.4]

        with self.assertRaises(ValueError):
            service.search_similar(
                query_embedding=query_embedding, topic_ids=[], limit=5
            )

    @patch("rag.retrieval.qdrant.QdrantClient")
    def test_search_similar_api_call(self, mock_qdrant_client: MagicMock) -> None:
        """Test that Qdrant search API is called correctly."""
        from rag.retrieval.qdrant import QdrantService

        # Mock the Qdrant client
        mock_client = MagicMock()
        mock_qdrant_client.return_value = mock_client

        # Mock search response
        mock_scored_point = MagicMock()
        mock_scored_point.id = self.context_item.id
        mock_scored_point.score = 0.95
        mock_scored_point.payload = {
            "context_item_id": self.context_item.id,
            "title": "Test Item",
            "content": "Test content",
        }

        mock_client.search.return_value = [mock_scored_point]

        service = QdrantService()
        query_embedding = [0.1, 0.2, 0.3, 0.4]
        topic_ids = [self.topic.id]

        results = service.search_similar(
            query_embedding=query_embedding, topic_ids=topic_ids, limit=5
        )

        # Verify the search API was called correctly
        mock_client.search.assert_called_once()
        call_args = mock_client.search.call_args[1]

        self.assertEqual(call_args["collection_name"], "context_items")
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
        from rag.retrieval.qdrant import QdrantService

        service = QdrantService()
        result = service.create_collection()

        self.assertTrue(result)

    @patch("rag.retrieval.qdrant.QdrantClient")
    def test_create_collection_api_call(self, mock_qdrant_client: MagicMock) -> None:
        """Test that collection creation API is called correctly."""
        from rag.retrieval.qdrant import QdrantService

        # Mock the Qdrant client
        mock_client = MagicMock()
        mock_qdrant_client.return_value = mock_client

        service = QdrantService()
        result = service.create_collection()

        # Verify the API was called correctly
        mock_client.create_collection.assert_called_once()
        call_args = mock_client.create_collection.call_args[1]

        self.assertEqual(call_args["collection_name"], "context_items")
        self.assertIn("vectors_config", call_args)

        self.assertTrue(result)


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

    @patch("rag.retrieval.reranking.CrossEncoder")
    def test_rerank_results_model_call(self, mock_cross_encoder: MagicMock) -> None:
        """Test that BGE reranking model is called correctly."""
        from rag.retrieval.reranking import RerankingService

        # Mock the CrossEncoder
        mock_model = MagicMock()
        mock_cross_encoder.return_value = mock_model
        mock_model.predict.return_value = [0.9, 0.3, 0.7]  # Rerank scores

        service = RerankingService()

        search_results = [
            {"context_item_id": 1, "content": "Machine learning content"},
            {"context_item_id": 2, "content": "Cooking recipes"},
            {"context_item_id": 3, "content": "Deep learning networks"},
        ]

        query = "machine learning"
        reranked_results = service.rerank_results(query, search_results)

        # Verify model was initialized correctly
        mock_cross_encoder.assert_called_once_with("BAAI/bge-reranker-base")

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

    @patch("rag.retrieval.reranking.CrossEncoder")
    def test_rerank_results_model_error(self, mock_cross_encoder: MagicMock) -> None:
        """Test handling of model errors during reranking."""
        from rag.retrieval.reranking import RerankingService

        # Mock the CrossEncoder to raise an exception
        mock_model = MagicMock()
        mock_cross_encoder.return_value = mock_model
        mock_model.predict.side_effect = Exception("Model error")

        service = RerankingService()
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

    @patch("rag.retrieval.rag.EmbeddingService")
    @patch("rag.retrieval.rag.QdrantService")
    @patch("rag.retrieval.rag.RerankingService")
    @patch("rag.retrieval.rag.OpenAI")
    def test_query_pipeline_orchestration(
        self,
        mock_openai: MagicMock,
        mock_reranking: MagicMock,
        mock_qdrant: MagicMock,
        mock_embedding: MagicMock,
    ) -> None:
        """Test that the complete RAG pipeline orchestrates all services correctly."""
        from rag.retrieval.rag import RAGService

        # Mock the embedding service
        mock_embedding_instance = MagicMock()
        mock_embedding.return_value = mock_embedding_instance
        mock_embedding_instance.generate_embedding.return_value = [0.1, 0.2, 0.3, 0.4]

        # Mock the Qdrant service
        mock_qdrant_instance = MagicMock()
        mock_qdrant.return_value = mock_qdrant_instance
        mock_qdrant_instance.search_similar.return_value = [
            {
                "context_item_id": self.context_item.id,
                "score": 0.9,
                "title": "Neural Networks",
                "content": "Neural networks are fundamental to deep learning.",
                "context_id": self.context.id,
                "context_type": "PDF",
            }
        ]

        # Mock the reranking service
        mock_reranking_instance = MagicMock()
        mock_reranking.return_value = mock_reranking_instance
        mock_reranking_instance.rerank_results.return_value = [
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

        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="Neural networks are computational models inspired by biological neural networks."
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response

        service = RAGService()
        query = "What are neural networks?"
        topic_ids = [self.topic.id]

        result = service.query(query, topic_ids)

        # Verify embedding service was called
        mock_embedding_instance.generate_embedding.assert_called_once_with(query)

        # Verify Qdrant search was called
        mock_qdrant_instance.search_similar.assert_called_once_with(
            query_embedding=[0.1, 0.2, 0.3, 0.4], topic_ids=topic_ids, limit=10
        )

        # Verify reranking was called
        mock_reranking_instance.rerank_results.assert_called_once()

        # Verify OpenAI was called
        mock_client.chat.completions.create.assert_called_once()

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

    @patch("rag.retrieval.rag.EmbeddingService")
    def test_query_embedding_service_error(self, mock_embedding: MagicMock) -> None:
        """Test handling of embedding service errors."""
        from rag.retrieval.rag import RAGService

        # Mock embedding service to raise an exception
        mock_embedding_instance = MagicMock()
        mock_embedding.return_value = mock_embedding_instance
        mock_embedding_instance.generate_embedding.side_effect = Exception(
            "Embedding error"
        )

        service = RAGService()

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
