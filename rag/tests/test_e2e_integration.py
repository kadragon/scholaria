"""End-to-end integration tests for the complete RAG system."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from django.test import TestCase

from rag.models import Context, ContextItem, Topic
from rag.retrieval.embeddings import EmbeddingService
from rag.retrieval.qdrant import QdrantService
from rag.retrieval.rag import RAGService
from rag.tasks import ingest_faq_document, ingest_markdown_document, ingest_pdf_document

if TYPE_CHECKING:
    pass


@pytest.mark.integration
@pytest.mark.slow
class EndToEndIngestionFlowTest(TestCase):
    """Test complete ingestion flow: upload → parse → embed → store."""

    def setUp(self) -> None:
        """Set up test data."""
        # Create test topic and context
        self.topic = Topic.objects.create(
            name="Test Topic",
            description="Test topic for E2E testing",
            system_prompt="You are a helpful assistant.",
        )

        self.context = Context.objects.create(
            name="Test Context",
            description="Test context for E2E testing",
            context_type="PDF",
        )

        # Associate topic with context
        self.topic.contexts.add(self.context)

        # Initialize services
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()

    def test_complete_pdf_ingestion_flow(self) -> None:
        """Test complete PDF ingestion: upload → parse → chunk → embed → store."""
        test_content = "This is a test PDF document. It contains important information about testing."

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.pdf"
            file_path.write_bytes(test_content.encode())

            # Mock external API boundaries
            with patch("rag.ingestion.parsers.PDFParser.parse_file") as mock_parse:
                mock_parse.return_value = test_content

                # Mock OpenAI API responses
                mock_embedding = [
                    0.1
                ] * 3072  # Proper embedding dimension for text-embedding-3-large
                mock_openai_response = MagicMock()
                mock_openai_response.data = [MagicMock()]
                mock_openai_response.data[0].embedding = mock_embedding

                with patch("openai.OpenAI") as MockOpenAI:
                    mock_client = MagicMock()
                    MockOpenAI.return_value = mock_client
                    mock_client.embeddings.create.return_value = mock_openai_response

                    # Mock Qdrant client
                    with patch("qdrant_client.QdrantClient") as MockQdrant:
                        mock_qdrant = MagicMock()
                        MockQdrant.return_value = mock_qdrant
                        mock_qdrant.upsert.return_value = MagicMock(
                            operation_id="test_op_123"
                        )

                        # Run PDF ingestion task
                        chunks_created = ingest_pdf_document.apply(
                            args=(self.context.id, str(file_path), "Test Document")
                        ).result

                        # Verify chunks were created in database
                        self.assertGreater(chunks_created, 0)
                        context_items = ContextItem.objects.filter(context=self.context)
                        self.assertEqual(context_items.count(), chunks_created)

                        # Verify chunk metadata
                        first_item = context_items.first()
                        self.assertIsNotNone(first_item)
                        assert first_item is not None
                        self.assertEqual(first_item.context, self.context)
                        self.assertEqual(first_item.file_path, str(file_path))
                        self.assertIsNotNone(first_item.metadata)
                        assert first_item.metadata is not None
                        self.assertIn("chunk_index", first_item.metadata)
                        self.assertIn("total_chunks", first_item.metadata)

                        # Verify the ingestion task completed successfully
                        mock_parse.assert_called_once_with(str(file_path))

                        # Now test the embedding pipeline separately (as it would be done manually/admin)
                        for item in context_items:
                            # Generate embedding using service (which will call mocked OpenAI)
                            embedding = self.embedding_service.generate_embedding(
                                item.content
                            )
                            self.assertEqual(len(embedding), 3072)

                            # Store in Qdrant using service (which will call mocked Qdrant)
                            operation_id = self.qdrant_service.store_embedding(
                                context_item_id=item.id,
                                embedding=embedding,
                                metadata={"ingestion_test": True},
                            )
                            self.assertIsNotNone(operation_id)

                        # Verify external APIs were called through services during embedding phase
                        self.assertEqual(
                            mock_client.embeddings.create.call_count, chunks_created
                        )
                        self.assertEqual(mock_qdrant.upsert.call_count, chunks_created)

    def test_complete_markdown_ingestion_flow(self) -> None:
        """Test complete Markdown ingestion: upload → parse → chunk → embed → store."""
        self.context.context_type = "MARKDOWN"
        self.context.save()

        test_content = """# Test Document

## Introduction
This is a test markdown document.

## Content
It contains multiple sections with important information.

### Subsection
More detailed information here.
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.md"
            file_path.write_text(test_content)

            # Mock external API boundaries
            mock_embedding = [0.5] * 3072
            mock_openai_response = MagicMock()
            mock_openai_response.data = [MagicMock()]
            mock_openai_response.data[0].embedding = mock_embedding

            with patch("openai.OpenAI") as MockOpenAI:
                mock_client = MagicMock()
                MockOpenAI.return_value = mock_client
                mock_client.embeddings.create.return_value = mock_openai_response

                with patch("qdrant_client.QdrantClient") as MockQdrant:
                    mock_qdrant = MagicMock()
                    MockQdrant.return_value = mock_qdrant
                    mock_qdrant.upsert.return_value = MagicMock(
                        operation_id="test_op_456"
                    )

                    # Run markdown ingestion task
                    chunks_created = ingest_markdown_document.apply(
                        args=(self.context.id, str(file_path), "Test Markdown")
                    ).result

                    # Verify results
                    self.assertGreater(chunks_created, 0)
                    context_items = ContextItem.objects.filter(context=self.context)
                    self.assertEqual(context_items.count(), chunks_created)

                    # Verify content was properly processed
                    first_item = context_items.first()
                    self.assertIsNotNone(first_item)
                    assert first_item is not None
                    self.assertIn("Test Document", first_item.content)

                    # Test embedding pipeline separately
                    for item in context_items:
                        embedding = self.embedding_service.generate_embedding(
                            item.content
                        )
                        self.assertEqual(len(embedding), 3072)

                        operation_id = self.qdrant_service.store_embedding(
                            context_item_id=item.id, embedding=embedding
                        )
                        self.assertIsNotNone(operation_id)

                    # Verify external APIs were called during embedding phase
                    self.assertEqual(
                        mock_client.embeddings.create.call_count, chunks_created
                    )
                    self.assertEqual(mock_qdrant.upsert.call_count, chunks_created)

    def test_complete_faq_ingestion_flow(self) -> None:
        """Test complete FAQ ingestion: upload → parse → chunk → embed → store."""
        self.context.context_type = "FAQ"
        self.context.save()

        test_content = """Q: What is the test system?
A: The test system is a comprehensive RAG pipeline for educational content.

Q: How does embedding work?
A: Embeddings are generated using OpenAI's text-embedding model and stored in Qdrant.

Q: What file types are supported?
A: The system supports PDF, Markdown, and FAQ file formats.
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.txt"
            file_path.write_text(test_content)

            # Mock external API boundaries
            mock_embedding = [0.9] * 3072
            mock_openai_response = MagicMock()
            mock_openai_response.data = [MagicMock()]
            mock_openai_response.data[0].embedding = mock_embedding

            with patch("openai.OpenAI") as MockOpenAI:
                mock_client = MagicMock()
                MockOpenAI.return_value = mock_client
                mock_client.embeddings.create.return_value = mock_openai_response

                with patch("qdrant_client.QdrantClient") as MockQdrant:
                    mock_qdrant = MagicMock()
                    MockQdrant.return_value = mock_qdrant
                    mock_qdrant.upsert.return_value = MagicMock(
                        operation_id="test_op_789"
                    )

                    # Run FAQ ingestion task
                    chunks_created = ingest_faq_document.apply(
                        args=(self.context.id, str(file_path), "Test FAQ")
                    ).result

                    # Verify results
                    self.assertGreater(chunks_created, 0)
                    context_items = ContextItem.objects.filter(context=self.context)
                    self.assertEqual(context_items.count(), chunks_created)

                    # Verify FAQ content was processed
                    all_content = " ".join([item.content for item in context_items])
                    self.assertIn("RAG pipeline", all_content)
                    self.assertIn("OpenAI", all_content)

                    # Test embedding pipeline separately
                    for item in context_items:
                        embedding = self.embedding_service.generate_embedding(
                            item.content
                        )
                        self.assertEqual(len(embedding), 3072)

                        operation_id = self.qdrant_service.store_embedding(
                            context_item_id=item.id, embedding=embedding
                        )
                        self.assertIsNotNone(operation_id)

                    # Verify external APIs were called during embedding phase
                    self.assertEqual(
                        mock_client.embeddings.create.call_count, chunks_created
                    )
                    self.assertEqual(mock_qdrant.upsert.call_count, chunks_created)

    def test_ingestion_error_handling(self) -> None:
        """Test error handling in the ingestion pipeline."""
        # Test with non-existent file - should raise FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            ingest_pdf_document.apply(
                args=(self.context.id, "/non/existent/file.pdf", "Non-existent")
            ).get(propagate=True)

        # Test with non-existent context
        with self.assertRaises(Context.DoesNotExist):
            ingest_pdf_document.apply(args=(99999, "dummy_file.pdf", "Dummy")).get(
                propagate=True
            )

    def test_embedding_service_integration(self) -> None:
        """Test embedding service integration with boundary mocking."""
        context_item = ContextItem.objects.create(
            title="Test Item",
            content="This is test content for embedding generation.",
            context=self.context,
        )

        # Mock OpenAI API boundary
        mock_embedding = [0.1] * 3072
        mock_openai_response = MagicMock()
        mock_openai_response.data = [MagicMock()]
        mock_openai_response.data[0].embedding = mock_embedding

        with patch("openai.OpenAI") as MockOpenAI:
            mock_client = MagicMock()
            MockOpenAI.return_value = mock_client
            mock_client.embeddings.create.return_value = mock_openai_response

            # Generate embedding through service (tests integration)
            embedding = self.embedding_service.generate_embedding(context_item.content)

            # Verify embedding properties
            self.assertEqual(len(embedding), 1536)
            self.assertTrue(all(isinstance(x, float) for x in embedding))
            mock_client.embeddings.create.assert_called_once()

    def test_qdrant_integration_flow(self) -> None:
        """Test Qdrant integration with boundary mocking."""
        context_item = ContextItem.objects.create(
            title="Qdrant Test Item",
            content="This content will be stored in Qdrant vector database.",
            context=self.context,
        )

        # Mock Qdrant client boundary
        with patch("qdrant_client.QdrantClient") as MockQdrant:
            mock_qdrant = MagicMock()
            MockQdrant.return_value = mock_qdrant
            mock_qdrant.upsert.return_value = MagicMock(
                operation_id="qdrant_operation_123"
            )

            # Store embedding through service (tests integration)
            test_embedding = [0.2] * 3072
            operation_id = self.qdrant_service.store_embedding(
                context_item_id=context_item.id,
                embedding=test_embedding,
                metadata={"test": "integration"},
            )

            # Verify operation
            self.assertEqual(operation_id, "qdrant_operation_123")
            mock_qdrant.upsert.assert_called_once()


@pytest.mark.integration
@pytest.mark.slow
class EndToEndQAFlowTest(TestCase):
    """Test complete Q&A flow: select topic → ask question → get answer."""

    def setUp(self) -> None:
        """Set up test data for Q&A flow."""
        # Create test topic and context
        self.topic = Topic.objects.create(
            name="Machine Learning",
            description="Course on machine learning fundamentals",
            system_prompt="You are an expert ML tutor. Provide clear, educational answers.",
        )

        self.context = Context.objects.create(
            name="ML Fundamentals",
            description="Basic machine learning concepts",
            context_type="MARKDOWN",
        )

        # Associate topic with context
        self.topic.contexts.add(self.context)

        # Create sample context items with ML content
        self.context_items = [
            ContextItem.objects.create(
                title="Neural Networks Basics",
                content="Neural networks are computational models inspired by biological neural networks. They consist of interconnected nodes (neurons) that process information through weighted connections.",
                context=self.context,
                metadata={"chunk_index": 1, "total_chunks": 3},
            ),
            ContextItem.objects.create(
                title="Supervised Learning",
                content="Supervised learning is a machine learning paradigm where algorithms learn from labeled training data to make predictions on new, unseen data.",
                context=self.context,
                metadata={"chunk_index": 2, "total_chunks": 3},
            ),
            ContextItem.objects.create(
                title="Deep Learning",
                content="Deep learning uses artificial neural networks with multiple layers to model complex patterns in data. It has revolutionized fields like computer vision and natural language processing.",
                context=self.context,
                metadata={"chunk_index": 3, "total_chunks": 3},
            ),
        ]

        # Initialize RAG service
        self.rag_service = RAGService()

    def test_complete_qa_flow_with_good_results(self) -> None:
        """Test complete Q&A flow: topic selection → question → answer with citations."""
        question = "What are neural networks and how do they work?"

        # Mock external API boundaries
        mock_query_embedding = [0.1] * 3072
        mock_search_results = [
            {
                "context_item_id": self.context_items[0].id,
                "title": self.context_items[0].title,
                "content": self.context_items[0].content,
                "score": 0.95,
                "context_type": "MARKDOWN",
                "context_id": self.context.id,
            },
            {
                "context_item_id": self.context_items[2].id,
                "title": self.context_items[2].title,
                "content": self.context_items[2].content,
                "score": 0.87,
                "context_type": "MARKDOWN",
                "context_id": self.context.id,
            },
        ]

        mock_answer = "Neural networks are computational models inspired by biological neural networks. They consist of interconnected nodes called neurons that process information through weighted connections. These networks can learn complex patterns in data by adjusting the weights during training."

        # Mock OpenAI API for embedding
        mock_openai_embed_response = MagicMock()
        mock_openai_embed_response.data = [MagicMock()]
        mock_openai_embed_response.data[0].embedding = mock_query_embedding

        # Mock OpenAI API for chat completion
        mock_chat_response = MagicMock()
        mock_chat_response.choices = [MagicMock()]
        mock_chat_response.choices[0].message.content = mock_answer

        # Mock BGE reranker
        mock_rerank_scores = [0.92, 0.85]  # Scores for the two search results

        with patch("openai.OpenAI") as MockOpenAI:
            mock_openai_client = MagicMock()
            MockOpenAI.return_value = mock_openai_client
            mock_openai_client.embeddings.create.return_value = (
                mock_openai_embed_response
            )
            mock_openai_client.chat.completions.create.return_value = mock_chat_response

            with patch("qdrant_client.QdrantClient") as MockQdrant:
                mock_qdrant = MagicMock()
                MockQdrant.return_value = mock_qdrant
                # Mock Qdrant search to return scored points
                mock_scored_points = []
                for result in mock_search_results:
                    mock_point = MagicMock()
                    mock_point.payload = {
                        "context_item_id": result["context_item_id"],
                        "title": result["title"],
                        "content": result["content"],
                        "context_id": result["context_id"],
                        "context_type": result["context_type"],
                    }
                    mock_point.score = result["score"]
                    mock_scored_points.append(mock_point)
                mock_qdrant.search.return_value = mock_scored_points

                with patch("sentence_transformers.CrossEncoder") as MockCrossEncoder:
                    mock_reranker = MagicMock()
                    MockCrossEncoder.return_value = mock_reranker
                    mock_reranker.predict.return_value = mock_rerank_scores

                    # Execute the complete Q&A flow
                    result = self.rag_service.query(
                        query=question, topic_ids=[self.topic.id]
                    )

                    # Verify the result structure
                    self.assertIn("answer", result)
                    self.assertIn("sources", result)
                    self.assertIn("context_items", result)

                    # Verify answer content
                    self.assertEqual(result["answer"], mock_answer)

                    # Verify sources/citations (should be sorted by rerank score)
                    sources = result["sources"]
                    assert isinstance(sources, list)  # Type assertion for mypy
                    self.assertGreater(len(sources), 0)
                    source = sources[0]
                    self.assertEqual(source["title"], "Neural Networks Basics")
                    self.assertEqual(
                        source["context_item_id"], self.context_items[0].id
                    )
                    self.assertEqual(source["context_type"], "MARKDOWN")

                    # Verify external APIs were called
                    mock_openai_client.embeddings.create.assert_called_once()
                    mock_openai_client.chat.completions.create.assert_called_once()
                    mock_reranker.predict.assert_called_once()

    def test_qa_flow_with_no_results(self) -> None:
        """Test Q&A flow when no relevant context is found."""
        question = "What is quantum computing?"

        # Mock external APIs for no results scenario
        mock_query_embedding = [0.1] * 3072
        mock_openai_embed_response = MagicMock()
        mock_openai_embed_response.data = [MagicMock()]
        mock_openai_embed_response.data[0].embedding = mock_query_embedding

        with patch("openai.OpenAI") as MockOpenAI:
            mock_openai_client = MagicMock()
            MockOpenAI.return_value = mock_openai_client
            mock_openai_client.embeddings.create.return_value = (
                mock_openai_embed_response
            )

            with patch("qdrant_client.QdrantClient") as MockQdrant:
                mock_qdrant = MagicMock()
                MockQdrant.return_value = mock_qdrant
                mock_qdrant.search.return_value = []  # No results found

                # Execute Q&A flow
                result = self.rag_service.query(
                    query=question, topic_ids=[self.topic.id]
                )

                # Verify appropriate response for no results
                self.assertIn(
                    "couldn't find any relevant information", result["answer"]
                )
                self.assertEqual(len(result["sources"]), 0)
                self.assertEqual(len(result["context_items"]), 0)

                # Verify embedding API was called but not chat API (since no results)
                mock_openai_client.embeddings.create.assert_called_once()
                mock_openai_client.chat.completions.create.assert_not_called()

    def test_qa_flow_with_multiple_topics(self) -> None:
        """Test Q&A flow with multiple topics selected."""
        # Create second topic and context
        topic2 = Topic.objects.create(
            name="Deep Learning",
            description="Advanced deep learning concepts",
            system_prompt="You are a deep learning expert.",
        )

        context2 = Context.objects.create(
            name="Deep Learning Advanced",
            description="Advanced DL concepts",
            context_type="PDF",
        )

        topic2.contexts.add(context2)

        question = "Explain deep learning applications"

        # Mock external APIs for multiple topics
        mock_query_embedding = [0.1] * 3072
        mock_search_results = [
            {
                "context_item_id": self.context_items[2].id,
                "title": self.context_items[2].title,
                "content": self.context_items[2].content,
                "score": 0.88,
                "context_type": "MARKDOWN",
                "context_id": self.context.id,
            }
        ]
        mock_answer = (
            "Deep learning has applications in computer vision, NLP, and more."
        )

        # Mock OpenAI APIs
        mock_openai_embed_response = MagicMock()
        mock_openai_embed_response.data = [MagicMock()]
        mock_openai_embed_response.data[0].embedding = mock_query_embedding

        mock_chat_response = MagicMock()
        mock_chat_response.choices = [MagicMock()]
        mock_chat_response.choices[0].message.content = mock_answer

        with patch("openai.OpenAI") as MockOpenAI:
            mock_openai_client = MagicMock()
            MockOpenAI.return_value = mock_openai_client
            mock_openai_client.embeddings.create.return_value = (
                mock_openai_embed_response
            )
            mock_openai_client.chat.completions.create.return_value = mock_chat_response

            with patch("qdrant_client.QdrantClient") as MockQdrant:
                mock_qdrant = MagicMock()
                MockQdrant.return_value = mock_qdrant
                # Mock Qdrant search to return scored points
                mock_scored_points = []
                for result in mock_search_results:
                    mock_point = MagicMock()
                    mock_point.payload = {
                        "context_item_id": result["context_item_id"],
                        "title": result["title"],
                        "content": result["content"],
                        "context_id": result["context_id"],
                        "context_type": result["context_type"],
                    }
                    mock_point.score = result["score"]
                    mock_scored_points.append(mock_point)
                mock_qdrant.search.return_value = mock_scored_points

                with patch("sentence_transformers.CrossEncoder") as MockCrossEncoder:
                    mock_reranker = MagicMock()
                    MockCrossEncoder.return_value = mock_reranker
                    mock_reranker.predict.return_value = [0.88]

                    # Execute with multiple topics
                    result = self.rag_service.query(
                        query=question, topic_ids=[self.topic.id, topic2.id]
                    )

                    # Verify result structure
                    self.assertIsInstance(result["answer"], str)
                    self.assertIsInstance(result["sources"], list)
                    self.assertEqual(result["answer"], mock_answer)

                    # Verify external APIs were called
                    mock_openai_client.embeddings.create.assert_called_once()
                    mock_openai_client.chat.completions.create.assert_called_once()
                    mock_reranker.predict.assert_called_once()

    def test_qa_flow_error_handling(self) -> None:
        """Test Q&A flow error handling scenarios."""
        # Test with empty query
        with self.assertRaises(ValueError):
            self.rag_service.query(query="", topic_ids=[self.topic.id])

        # Test with None query
        with self.assertRaises(ValueError):
            self.rag_service.query(query=None, topic_ids=[self.topic.id])

        # Test with empty topic IDs
        with self.assertRaises(ValueError):
            self.rag_service.query(query="test question", topic_ids=[])

    def test_api_endpoint_integration(self) -> None:
        """Test the complete Q&A flow through the API endpoint."""
        import json

        from django.test import Client

        client = Client()

        # Mock the RAG service response
        mock_rag_result = {
            "answer": "Neural networks are computational models that learn patterns in data.",
            "sources": [
                {
                    "title": "Neural Networks Basics",
                    "content": "Neural networks are computational models...",
                    "score": 0.95,
                    "context_type": "MARKDOWN",
                    "context_item_id": self.context_items[0].id,
                }
            ],
            "context_items": [],
        }

        with patch("rag.views.RAGService") as mock_rag_class:
            mock_rag_instance = mock_rag_class.return_value
            mock_rag_instance.query.return_value = mock_rag_result

            # Make API request
            response = client.post(
                "/api/ask/",
                data=json.dumps(
                    {"topic_id": self.topic.id, "question": "What are neural networks?"}
                ),
                content_type="application/json",
            )

            # Verify response
            self.assertEqual(response.status_code, 200)
            response_data = response.json()

            self.assertIn("answer", response_data)
            self.assertIn("citations", response_data)
            self.assertIn("topic_id", response_data)
            self.assertEqual(response_data["topic_id"], self.topic.id)

            # Verify RAG service was called correctly
            mock_rag_instance.query.assert_called_once_with(
                query="What are neural networks?", topic_ids=[self.topic.id]
            )

            # Verify citation format
            citations = response_data["citations"]
            self.assertEqual(len(citations), 1)
            citation = citations[0]
            self.assertEqual(citation["title"], "Neural Networks Basics")
            self.assertEqual(citation["score"], 0.95)
            self.assertEqual(citation["context_type"], "MARKDOWN")

    def test_topic_selection_integration(self) -> None:
        """Test topic selection through the API."""
        from django.test import Client

        client = Client()

        # Test topic list endpoint
        response = client.get("/api/topics/")
        self.assertEqual(response.status_code, 200)

        topics_data = response.json()
        self.assertGreaterEqual(len(topics_data), 1)

        # Find our test topic
        test_topic = next(
            (topic for topic in topics_data if topic["id"] == self.topic.id), None
        )
        self.assertIsNotNone(test_topic)
        assert test_topic is not None  # Type assertion for mypy
        self.assertEqual(test_topic["name"], "Machine Learning")

        # Test topic detail endpoint
        response = client.get(f"/api/topics/{self.topic.id}/")
        self.assertEqual(response.status_code, 200)

        topic_detail = response.json()
        self.assertEqual(topic_detail["id"], self.topic.id)
        self.assertEqual(topic_detail["name"], "Machine Learning")
        self.assertEqual(
            topic_detail["description"], "Course on machine learning fundamentals"
        )
        self.assertEqual(
            topic_detail["system_prompt"],
            "You are an expert ML tutor. Provide clear, educational answers.",
        )
        self.assertIn("created_at", topic_detail)
        self.assertIn("updated_at", topic_detail)


@pytest.mark.integration
@pytest.mark.slow
class EndToEndAdminWorkflowTest(TestCase):
    """Test complete admin workflow: create topic → upload docs → map contexts."""

    def setUp(self) -> None:
        """Set up test data for admin workflow."""
        # Create a superuser for admin access
        from django.contrib.auth.models import User

        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@test.com", password="testpass123"
        )

    def test_complete_admin_workflow(self) -> None:
        """Test complete admin workflow: topic creation → context creation → file upload → mapping."""
        from django.test import Client

        client = Client()

        # Step 1: Admin login
        login_success = client.login(username="admin", password="testpass123")
        self.assertTrue(login_success)

        # Step 2: Create a new topic via admin interface
        topic_data = {
            "name": "Artificial Intelligence",
            "description": "Course on AI fundamentals and applications",
            "system_prompt": "You are an AI tutor providing clear explanations about artificial intelligence concepts.",
        }

        response = client.post("/admin/rag/topic/add/", data=topic_data)
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful creation

        # Verify topic was created
        topic = Topic.objects.get(name="Artificial Intelligence")
        self.assertEqual(
            topic.description, "Course on AI fundamentals and applications"
        )

        # Step 3: Create a context for holding documents
        context_data = {
            "name": "AI Fundamentals Documents",
            "description": "Collection of fundamental AI documents and papers",
            "context_type": "PDF",
        }

        response = client.post("/admin/rag/context/add/", data=context_data)
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful creation

        # Verify context was created
        context = Context.objects.get(name="AI Fundamentals Documents")
        self.assertEqual(context.context_type, "PDF")

        # Step 4: Upload a document via ContextItem admin
        from django.core.files.uploadedfile import SimpleUploadedFile

        # Create a test PDF file content
        test_pdf_content = (
            b"This is a test PDF content about neural networks and machine learning."
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = Path(temp_dir) / "ai_fundamentals.pdf"
            temp_file_path.write_bytes(test_pdf_content)

            # Create an uploaded file
            uploaded_file = SimpleUploadedFile(
                "ai_fundamentals.pdf", test_pdf_content, content_type="application/pdf"
            )

            context_item_data = {
                "title": "AI Fundamentals Chapter 1",
                "context": context.id,
                "content": "Introduction to artificial intelligence and neural networks.",
                "uploaded_file": uploaded_file,
            }

            # Mock the file validation and MinIO upload
            with patch("rag.admin.FileValidator") as mock_validator_class:
                mock_validator = mock_validator_class.return_value
                mock_validation_result = type(
                    "MockValidationResult",
                    (),
                    {"is_valid": True, "file_type": "pdf", "errors": []},
                )()
                mock_validator.validate_file.return_value = mock_validation_result
                mock_validator.sanitize_filename.return_value = "ai_fundamentals.pdf"

                with patch("rag.admin.MinIOStorage") as mock_storage_class:
                    mock_storage = mock_storage_class.return_value
                    mock_storage.ensure_bucket_exists.return_value = None
                    mock_storage.upload_django_file.return_value = "ai_fundamentals.pdf"

                    response = client.post(
                        "/admin/rag/contextitem/add/", data=context_item_data
                    )
                    self.assertEqual(
                        response.status_code, 302
                    )  # Redirect after successful creation

            # Verify context item was created
            context_item = ContextItem.objects.get(title="AI Fundamentals Chapter 1")
            self.assertEqual(context_item.context, context)
            self.assertIsNotNone(context_item.uploaded_file)

        # Step 5: Map context to topic via topic admin
        # First, get the topic change form
        response = client.get(f"/admin/rag/topic/{topic.id}/change/")
        self.assertEqual(response.status_code, 200)

        # Update topic to include the context
        topic_update_data = {
            "name": topic.name,
            "description": topic.description,
            "system_prompt": topic.system_prompt,
            "contexts": [context.id],  # Map the context to this topic
        }

        response = client.post(
            f"/admin/rag/topic/{topic.id}/change/", data=topic_update_data
        )
        self.assertEqual(response.status_code, 302)  # Redirect after successful update

        # Step 6: Verify the complete workflow
        # Reload topic and verify context mapping
        topic.refresh_from_db()
        self.assertIn(context, topic.contexts.all())

        # Verify we can query the context items through the topic
        topic_context_items = ContextItem.objects.filter(
            context__in=topic.contexts.all()
        )
        self.assertEqual(topic_context_items.count(), 1)
        first_topic_item = topic_context_items.first()
        self.assertIsNotNone(first_topic_item)
        assert first_topic_item is not None  # Type assertion for mypy
        self.assertEqual(first_topic_item.title, "AI Fundamentals Chapter 1")

        # Step 7: Test the complete data chain
        # Topic -> Context -> ContextItem with uploaded file
        self.assertEqual(topic.contexts.count(), 1)
        self.assertEqual(context.items.count(), 1)
        first_context_item = context.items.first()
        self.assertIsNotNone(first_context_item)
        assert first_context_item is not None  # Type assertion for mypy
        self.assertIsNotNone(first_context_item.uploaded_file)

    def test_admin_bulk_operations_workflow(self) -> None:
        """Test admin bulk operations in the complete workflow."""
        from django.test import Client

        client = Client()
        client.login(username="admin", password="testpass123")

        # Create test data: multiple topics and contexts
        topics = [
            Topic.objects.create(
                name=f"Topic {i}",
                description=f"Description for topic {i}",
                system_prompt=f"System prompt for topic {i}",
            )
            for i in range(1, 4)
        ]

        contexts = [
            Context.objects.create(
                name=f"Context {i}",
                description=f"Description for context {i}",
                context_type="MARKDOWN",
            )
            for i in range(1, 3)
        ]

        # Test bulk assignment of context to multiple topics
        bulk_assign_data = {
            "action": "assign_context_to_topics",
            "_selected_action": [str(topic.id) for topic in topics[:2]],
            "context_id": str(contexts[0].id),
        }

        response = client.post("/admin/rag/topic/", data=bulk_assign_data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Verify bulk assignment worked
        for topic in topics[:2]:
            topic.refresh_from_db()
            self.assertIn(contexts[0], topic.contexts.all())

        # Test bulk system prompt update
        new_prompt = "Updated system prompt for all selected topics"
        bulk_prompt_data = {
            "action": "bulk_update_system_prompt",
            "_selected_action": [str(topic.id) for topic in topics],
            "system_prompt": new_prompt,
        }

        response = client.post("/admin/rag/topic/", data=bulk_prompt_data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Verify bulk prompt update worked
        for topic in topics:
            topic.refresh_from_db()
            self.assertEqual(topic.system_prompt, new_prompt)

    def test_admin_file_upload_and_validation_workflow(self) -> None:
        """Test file upload validation workflow in admin."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test import Client

        client = Client()
        client.login(username="admin", password="testpass123")

        # Create prerequisite objects
        context = Context.objects.create(
            name="Test Context",
            description="Test context for file upload",
            context_type="PDF",
        )

        # Test 1: Valid file upload
        valid_pdf = SimpleUploadedFile(
            "valid_document.pdf", b"PDF content here", content_type="application/pdf"
        )

        with patch("rag.admin.FileValidator") as mock_validator_class:
            mock_validator = mock_validator_class.return_value
            mock_validation_result = type(
                "MockValidationResult",
                (),
                {"is_valid": True, "file_type": "pdf", "errors": []},
            )()
            mock_validator.validate_file.return_value = mock_validation_result
            mock_validator.sanitize_filename.return_value = "valid_document.pdf"

            with patch("rag.admin.MinIOStorage") as mock_storage_class:
                mock_storage = mock_storage_class.return_value
                mock_storage.ensure_bucket_exists.return_value = None
                mock_storage.upload_django_file.return_value = "valid_document.pdf"

                valid_upload_data = {
                    "title": "Valid Document",
                    "context": context.id,
                    "uploaded_file": valid_pdf,
                }

                response = client.post(
                    "/admin/rag/contextitem/add/", data=valid_upload_data
                )
                self.assertEqual(response.status_code, 302)

            # Verify the item was created
            self.assertTrue(ContextItem.objects.filter(title="Valid Document").exists())

        # Test 2: Invalid file upload (should be rejected)
        invalid_file = SimpleUploadedFile(
            "malicious.exe",
            b"Malicious content",
            content_type="application/octet-stream",
        )

        with patch("rag.admin.FileValidator") as mock_validator_class:
            mock_validator = mock_validator_class.return_value
            mock_validation_result = type(
                "MockValidationResult",
                (),
                {"is_valid": False, "file_type": None, "errors": ["Invalid file type"]},
            )()
            mock_validator.validate_file.return_value = mock_validation_result

            invalid_upload_data = {
                "title": "Invalid Document",
                "context": context.id,
                "uploaded_file": invalid_file,
            }

            response = client.post(
                "/admin/rag/contextitem/add/", data=invalid_upload_data
            )

            # Should show form with validation errors (not redirect)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "File validation failed")

            # Verify the item was NOT created
            self.assertFalse(
                ContextItem.objects.filter(title="Invalid Document").exists()
            )

    def test_admin_context_item_management_workflow(self) -> None:
        """Test context item management operations in admin."""
        from django.test import Client

        client = Client()
        client.login(username="admin", password="testpass123")

        # Create test data
        context1 = Context.objects.create(
            name="Source Context",
            description="Source context for items",
            context_type="MARKDOWN",
        )

        context2 = Context.objects.create(
            name="Target Context",
            description="Target context for moving items",
            context_type="MARKDOWN",
        )

        # Create context items
        items = [
            ContextItem.objects.create(
                title=f"Item {i}", content=f"Content for item {i}", context=context1
            )
            for i in range(1, 4)
        ]

        # Test bulk move operation
        bulk_move_data = {
            "action": "bulk_move_to_context",
            "_selected_action": [str(item.id) for item in items[:2]],
            "context_id": str(context2.id),
        }

        response = client.post(
            "/admin/rag/contextitem/", data=bulk_move_data, follow=True
        )
        self.assertEqual(response.status_code, 200)

        # Verify items were moved
        for item in items[:2]:
            item.refresh_from_db()
            self.assertEqual(item.context, context2)

        # Verify remaining item stayed in original context
        items[2].refresh_from_db()
        self.assertEqual(items[2].context, context1)

        # Test bulk embedding regeneration
        bulk_regen_data = {
            "action": "bulk_regenerate_embeddings",
            "_selected_action": [str(item.id) for item in items],
            "confirm": "yes",
        }

        response = client.post(
            "/admin/rag/contextitem/", data=bulk_regen_data, follow=True
        )
        self.assertEqual(response.status_code, 200)

        # Should see success message
        self.assertContains(response, "Scheduled embedding regeneration")

    def test_admin_workflow_error_handling(self) -> None:
        """Test error handling in admin workflow."""
        from django.test import Client

        client = Client()
        client.login(username="admin", password="testpass123")

        # Test 1: Create topic with missing required fields
        incomplete_topic_data = {
            "name": "",  # Missing required name
            "description": "Test description",
        }

        response = client.post("/admin/rag/topic/add/", data=incomplete_topic_data)
        self.assertEqual(response.status_code, 200)  # Form redisplayed with errors
        self.assertContains(response, "This field is required")

        # Test 2: Create context item without content or file
        context = Context.objects.create(
            name="Test Context", description="Test context", context_type="PDF"
        )

        invalid_item_data = {
            "title": "Test Item",
            "context": context.id,
            # Missing both content and uploaded_file
        }

        response = client.post("/admin/rag/contextitem/add/", data=invalid_item_data)
        self.assertEqual(response.status_code, 200)  # Form redisplayed with errors

        # Test 3: Invalid context type
        invalid_context_data = {
            "name": "Invalid Context",
            "description": "Test description",
            "context_type": "INVALID",  # Not a valid choice
        }

        response = client.post("/admin/rag/context/add/", data=invalid_context_data)
        self.assertEqual(response.status_code, 200)  # Form redisplayed with errors

    def test_admin_permissions_and_security(self) -> None:
        """Test admin permissions and security measures."""
        from django.contrib.auth.models import User
        from django.test import Client

        # Test 1: Unauthenticated access should be denied
        client = Client()

        response = client.get("/admin/rag/topic/")
        self.assertEqual(response.status_code, 302)  # Redirect to login

        response = client.get("/admin/rag/context/")
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test 2: Non-staff user should be denied
        User.objects.create_user(
            username="regular", email="regular@test.com", password="testpass123"
        )

        client.login(username="regular", password="testpass123")
        response = client.get("/admin/rag/topic/")
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test 3: Staff user with permissions should have access
        from django.contrib.auth.models import Permission

        staff_user = User.objects.create_user(
            username="staff",
            email="staff@test.com",
            password="testpass123",
            is_staff=True,
        )

        # Give staff user permissions to view topics
        view_topic_permission = Permission.objects.get(codename="view_topic")
        staff_user.user_permissions.add(view_topic_permission)

        client.login(username="staff", password="testpass123")
        response = client.get("/admin/rag/topic/")
        self.assertEqual(response.status_code, 200)  # Access granted
