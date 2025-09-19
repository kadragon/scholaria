"""Tests for golden dataset quality validation."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from django.test import TestCase

from rag.models import Context, ContextItem, Topic
from rag.retrieval.rag import RAGService

if TYPE_CHECKING:
    pass


class GoldenDatasetTest(TestCase):
    """Test golden dataset for quality validation."""

    def setUp(self) -> None:
        """Set up test data."""
        # Create test topic and context
        self.topic = Topic.objects.create(
            name="Machine Learning",
            description="Comprehensive machine learning course",
            system_prompt="You are an expert ML tutor. Provide accurate, educational answers with clear explanations.",
        )

        self.context = Context.objects.create(
            name="ML Fundamentals",
            description="Core machine learning concepts",
            context_type="MARKDOWN",
        )

        # Associate topic with context
        self.topic.contexts.add(self.context)

        # Create context items with realistic ML content
        self.context_items = [
            ContextItem.objects.create(
                title="Neural Networks Introduction",
                content="Neural networks are computational models inspired by biological neural networks. They consist of interconnected nodes (neurons) organized in layers. Each connection has a weight that adjusts during training. The network learns by adjusting these weights through backpropagation to minimize prediction errors.",
                context=self.context,
                metadata={"chunk_index": 1, "total_chunks": 5},
            ),
            ContextItem.objects.create(
                title="Supervised Learning Overview",
                content="Supervised learning is a machine learning paradigm where algorithms learn from labeled training data. The goal is to create a mapping function from input features to target outputs. Common supervised learning tasks include classification (predicting categories) and regression (predicting continuous values).",
                context=self.context,
                metadata={"chunk_index": 2, "total_chunks": 5},
            ),
            ContextItem.objects.create(
                title="Deep Learning Fundamentals",
                content="Deep learning uses artificial neural networks with multiple hidden layers to model complex patterns in data. Deep networks can automatically learn hierarchical feature representations from raw data. They have achieved breakthrough results in computer vision, natural language processing, and speech recognition.",
                context=self.context,
                metadata={"chunk_index": 3, "total_chunks": 5},
            ),
            ContextItem.objects.create(
                title="Training and Optimization",
                content="Machine learning models are trained using optimization algorithms like gradient descent. The training process involves iteratively adjusting model parameters to minimize a loss function. Key concepts include learning rate, batch size, epochs, and regularization to prevent overfitting.",
                context=self.context,
                metadata={"chunk_index": 4, "total_chunks": 5},
            ),
            ContextItem.objects.create(
                title="Model Evaluation",
                content="Model evaluation involves assessing performance using metrics like accuracy, precision, recall, and F1-score for classification, or MAE and RMSE for regression. Cross-validation techniques help estimate model performance on unseen data and detect overfitting.",
                context=self.context,
                metadata={"chunk_index": 5, "total_chunks": 5},
            ),
        ]

        self.rag_service = RAGService()

    def test_golden_dataset_exists(self) -> None:
        """Test that golden dataset file exists."""
        from rag.tests.golden_dataset import GoldenDataset

        dataset = GoldenDataset()
        self.assertIsNotNone(dataset)
        self.assertTrue(hasattr(dataset, "load_dataset"))
        self.assertTrue(hasattr(dataset, "get_test_cases"))

    def test_golden_dataset_structure(self) -> None:
        """Test that golden dataset has proper structure."""
        from rag.tests.golden_dataset import GoldenDataset

        dataset = GoldenDataset()
        test_cases = dataset.get_test_cases()

        # Should have multiple test cases
        self.assertGreater(len(test_cases), 0)

        # Each test case should have required fields
        for case in test_cases:
            self.assertIn("question", case)
            self.assertIn("expected_keywords", case)
            self.assertIn("expected_topics", case)
            self.assertIn("difficulty", case)
            self.assertIn("category", case)

            # Validate field types
            self.assertIsInstance(case["question"], str)
            self.assertIsInstance(case["expected_keywords"], list)
            self.assertIsInstance(case["expected_topics"], list)
            self.assertIsInstance(case["difficulty"], str)
            self.assertIsInstance(case["category"], str)

            # Question should be non-empty
            self.assertGreater(len(case["question"]), 0)

            # Difficulty should be valid
            self.assertIn(case["difficulty"], ["easy", "medium", "hard"])

    def test_golden_dataset_quality_validation(self) -> None:
        """Test quality validation using golden dataset."""
        from rag.tests.golden_dataset import validate_rag_quality

        # Mock external API calls
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
                "context_item_id": self.context_items[1].id,
                "title": self.context_items[1].title,
                "content": self.context_items[1].content,
                "score": 0.87,
                "context_type": "MARKDOWN",
                "context_id": self.context.id,
            },
        ]

        mock_answer = "Neural networks are computational models inspired by biological neural networks. They consist of interconnected nodes organized in layers with weighted connections that adjust during training through backpropagation."

        # Mock all external APIs
        with patch("openai.OpenAI") as MockOpenAI:
            mock_openai_client = MagicMock()
            MockOpenAI.return_value = mock_openai_client

            # Mock embedding API
            mock_openai_embed_response = MagicMock()
            mock_openai_embed_response.data = [MagicMock()]
            mock_openai_embed_response.data[0].embedding = mock_query_embedding
            mock_openai_client.embeddings.create.return_value = (
                mock_openai_embed_response
            )

            # Mock chat completion API
            mock_chat_response = MagicMock()
            mock_chat_response.choices = [MagicMock()]
            mock_chat_response.choices[0].message.content = mock_answer
            mock_openai_client.chat.completions.create.return_value = mock_chat_response

            with patch("qdrant_client.QdrantClient") as MockQdrant:
                mock_qdrant = MagicMock()
                MockQdrant.return_value = mock_qdrant

                # Mock Qdrant search
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
                    mock_reranker.predict.return_value = [0.92, 0.85]

                    # Run quality validation
                    results = validate_rag_quality(
                        rag_service=self.rag_service,
                        topic_ids=[self.topic.id],
                        max_test_cases=3,  # Test with subset for faster execution
                    )

                    # Validate results structure
                    self.assertIn("overall_score", results)
                    self.assertIn("test_results", results)
                    self.assertIn("summary", results)

                    # Overall score should be between 0 and 1
                    self.assertGreaterEqual(results["overall_score"], 0.0)
                    self.assertLessEqual(results["overall_score"], 1.0)

                    # Should have test results
                    test_results = results["test_results"]
                    self.assertGreater(len(test_results), 0)

                    # Each test result should have proper structure
                    for result_dict in test_results:
                        self.assertIn("question", result_dict)
                        self.assertIn("answer", result_dict)
                        self.assertIn("keyword_score", result_dict)
                        self.assertIn("relevance_score", result_dict)
                        self.assertIn("passed", result_dict)

                        # Scores should be valid
                        self.assertGreaterEqual(result_dict["keyword_score"], 0.0)
                        self.assertLessEqual(result_dict["keyword_score"], 1.0)
                        self.assertGreaterEqual(result_dict["relevance_score"], 0.0)
                        self.assertLessEqual(result_dict["relevance_score"], 1.0)

    def test_golden_dataset_benchmark_categories(self) -> None:
        """Test that golden dataset covers different categories and difficulties."""
        from rag.tests.golden_dataset import GoldenDataset

        dataset = GoldenDataset()
        test_cases = dataset.get_test_cases()

        # Extract categories and difficulties
        categories = {case["category"] for case in test_cases}
        difficulties = {case["difficulty"] for case in test_cases}

        # Should have multiple categories
        self.assertGreaterEqual(len(categories), 3)
        expected_categories = {"fundamentals", "algorithms", "applications"}
        self.assertTrue(expected_categories.issubset(categories))

        # Should have all difficulty levels
        expected_difficulties = {"easy", "medium", "hard"}
        self.assertEqual(difficulties, expected_difficulties)

    def test_quality_validation_performance_tracking(self) -> None:
        """Test that quality validation tracks performance metrics."""
        from rag.tests.golden_dataset import validate_rag_quality

        # Mock a simpler scenario for performance testing
        mock_query_embedding = [0.1] * 3072
        mock_search_results = [
            {
                "context_item_id": self.context_items[0].id,
                "title": self.context_items[0].title,
                "content": self.context_items[0].content,
                "score": 0.95,
                "context_type": "MARKDOWN",
                "context_id": self.context.id,
            }
        ]

        mock_answer = (
            "Neural networks are computational models with interconnected nodes."
        )

        with patch("openai.OpenAI") as MockOpenAI:
            mock_openai_client = MagicMock()
            MockOpenAI.return_value = mock_openai_client

            mock_openai_embed_response = MagicMock()
            mock_openai_embed_response.data = [MagicMock()]
            mock_openai_embed_response.data[0].embedding = mock_query_embedding
            mock_openai_client.embeddings.create.return_value = (
                mock_openai_embed_response
            )

            mock_chat_response = MagicMock()
            mock_chat_response.choices = [MagicMock()]
            mock_chat_response.choices[0].message.content = mock_answer
            mock_openai_client.chat.completions.create.return_value = mock_chat_response

            with patch("qdrant_client.QdrantClient") as MockQdrant:
                mock_qdrant = MagicMock()
                MockQdrant.return_value = mock_qdrant

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
                    mock_reranker.predict.return_value = [0.90]

                    # Run validation and check performance metrics
                    results = validate_rag_quality(
                        rag_service=self.rag_service,
                        topic_ids=[self.topic.id],
                        max_test_cases=1,
                    )

                    # Should track response times
                    summary = results["summary"]
                    self.assertIn("avg_response_time", summary)
                    self.assertIn("total_test_cases", summary)
                    self.assertIn("passed_tests", summary)
                    self.assertIn("failed_tests", summary)

                    # Performance metrics should be reasonable
                    self.assertGreater(summary["avg_response_time"], 0.0)
                    self.assertEqual(summary["total_test_cases"], 1)
                    self.assertEqual(
                        summary["passed_tests"] + summary["failed_tests"], 1
                    )
