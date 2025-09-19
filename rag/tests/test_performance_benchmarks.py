"""Performance benchmarks for RAG system with < 3 second response time requirement."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from django.test import TestCase

from rag.models import Context, ContextItem, Topic
from rag.retrieval.rag import RAGService

if TYPE_CHECKING:
    pass


class PerformanceBenchmarkTest(TestCase):
    """Test performance benchmarks for RAG system."""

    def setUp(self) -> None:
        """Set up test data for performance benchmarking."""
        # Create test topic and context
        self.topic = Topic.objects.create(
            name="Computer Science",
            description="Computer science fundamentals and programming",
            system_prompt="You are a computer science tutor. Provide clear, technical explanations.",
        )

        self.context = Context.objects.create(
            name="Programming Concepts",
            description="Basic programming and CS concepts",
            context_type="MARKDOWN",
        )

        # Associate topic with context
        self.topic.contexts.add(self.context)

        # Create realistic context items for performance testing
        self.context_items = [
            ContextItem.objects.create(
                title="Data Structures Overview",
                content="Data structures are fundamental concepts in computer science that organize and store data efficiently. Common data structures include arrays, linked lists, stacks, queues, trees, and hash tables. Each has specific use cases and performance characteristics for different operations like insertion, deletion, and search.",
                context=self.context,
                metadata={"chunk_index": 1, "total_chunks": 8},
            ),
            ContextItem.objects.create(
                title="Algorithms and Complexity",
                content="Algorithms are step-by-step procedures for solving computational problems. Algorithm analysis involves studying time and space complexity using Big O notation. Common algorithmic paradigms include divide and conquer, dynamic programming, greedy algorithms, and graph algorithms.",
                context=self.context,
                metadata={"chunk_index": 2, "total_chunks": 8},
            ),
            ContextItem.objects.create(
                title="Object-Oriented Programming",
                content="Object-oriented programming (OOP) is a programming paradigm based on objects that contain data (attributes) and code (methods). Key OOP concepts include encapsulation, inheritance, polymorphism, and abstraction. These principles help create modular, reusable, and maintainable code.",
                context=self.context,
                metadata={"chunk_index": 3, "total_chunks": 8},
            ),
            ContextItem.objects.create(
                title="Database Systems",
                content="Database systems manage the storage, retrieval, and organization of data. Relational databases use SQL for querying structured data with ACID properties. NoSQL databases handle unstructured data and provide horizontal scalability. Key concepts include normalization, indexing, and transaction management.",
                context=self.context,
                metadata={"chunk_index": 4, "total_chunks": 8},
            ),
            ContextItem.objects.create(
                title="Network Programming",
                content="Network programming involves communication between distributed systems. The TCP/IP protocol stack provides reliable data transmission over networks. HTTP/HTTPS protocols enable web communication. Socket programming allows low-level network communication between applications.",
                context=self.context,
                metadata={"chunk_index": 5, "total_chunks": 8},
            ),
            ContextItem.objects.create(
                title="Software Engineering",
                content="Software engineering encompasses the systematic approach to designing, developing, and maintaining large-scale software systems. Key practices include version control, testing methodologies, design patterns, agile development, and continuous integration/deployment.",
                context=self.context,
                metadata={"chunk_index": 6, "total_chunks": 8},
            ),
            ContextItem.objects.create(
                title="Computer Architecture",
                content="Computer architecture deals with the design and organization of computer systems. Key components include CPU, memory hierarchy, input/output systems, and instruction set architectures. Performance optimization involves understanding cache behavior, pipelining, and parallel processing.",
                context=self.context,
                metadata={"chunk_index": 7, "total_chunks": 8},
            ),
            ContextItem.objects.create(
                title="Operating Systems",
                content="Operating systems manage computer hardware resources and provide services to applications. Core concepts include process management, memory management, file systems, and concurrency control. Modern OS features include virtual memory, multithreading, and security mechanisms.",
                context=self.context,
                metadata={"chunk_index": 8, "total_chunks": 8},
            ),
        ]

        self.rag_service = RAGService()

    def test_performance_benchmark_module_exists(self) -> None:
        """Test that performance benchmark module exists."""
        from rag.tests.performance_benchmarks import PerformanceBenchmark

        benchmark = PerformanceBenchmark()
        self.assertIsNotNone(benchmark)
        self.assertTrue(hasattr(benchmark, "run_benchmarks"))
        self.assertTrue(hasattr(benchmark, "measure_response_time"))
        self.assertTrue(hasattr(benchmark, "generate_performance_report"))

    def test_single_query_response_time_under_3_seconds(self) -> None:
        """Test that a single RAG query responds within 3 seconds."""
        from rag.tests.performance_benchmarks import PerformanceBenchmark

        # Mock external API calls to focus on system performance
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

        mock_answer = "Data structures are fundamental concepts that organize and store data efficiently, including arrays, linked lists, and hash tables."

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

                    # Measure response time
                    benchmark = PerformanceBenchmark()
                    response_time = benchmark.measure_response_time(
                        rag_service=self.rag_service,
                        query="What are data structures?",
                        topic_ids=[self.topic.id],
                    )

                    # Verify response time is under 3 seconds
                    self.assertLess(
                        response_time,
                        3.0,
                        f"Response time {response_time:.2f}s exceeds 3 second requirement",
                    )
                    self.assertGreater(response_time, 0.0)

    def test_concurrent_queries_performance(self) -> None:
        """Test performance under concurrent query load."""
        from rag.tests.performance_benchmarks import PerformanceBenchmark

        # Mock external APIs for consistency
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

        mock_answer = "Concurrent programming involves multiple execution paths."

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

                    # Test concurrent performance
                    benchmark = PerformanceBenchmark()
                    concurrent_results = benchmark.run_concurrent_benchmark(
                        rag_service=self.rag_service,
                        queries=[
                            "What are algorithms?",
                            "Explain object-oriented programming",
                            "How do databases work?",
                        ],
                        topic_ids=[self.topic.id],
                        concurrent_users=3,
                    )

                    # Verify all queries completed
                    self.assertEqual(len(concurrent_results), 3)

                    # Verify all response times are under 3 seconds
                    for result_dict in concurrent_results:
                        self.assertIn("response_time", result_dict)
                        self.assertIn("query", result_dict)
                        self.assertIn("success", result_dict)
                        self.assertLess(
                            result_dict["response_time"],
                            3.0,
                            f"Concurrent query '{result_dict['query']}' took {result_dict['response_time']:.2f}s",
                        )

    def test_load_testing_benchmark(self) -> None:
        """Test system performance under sustained load."""
        from rag.tests.performance_benchmarks import PerformanceBenchmark

        # Mock external APIs
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

        mock_answer = "Load testing measures system performance under stress."

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

                    # Run load test
                    benchmark = PerformanceBenchmark()
                    load_results = benchmark.run_load_test(
                        rag_service=self.rag_service,
                        query="What is load testing?",
                        topic_ids=[self.topic.id],
                        num_requests=10,
                        duration_seconds=5,
                    )

                    # Verify load test results
                    self.assertIn("total_requests", load_results)
                    self.assertIn("successful_requests", load_results)
                    self.assertIn("failed_requests", load_results)
                    self.assertIn("avg_response_time", load_results)
                    self.assertIn("p95_response_time", load_results)
                    self.assertIn("p99_response_time", load_results)
                    self.assertIn("requests_per_second", load_results)

                    # Verify performance requirements
                    self.assertGreater(load_results["total_requests"], 0)
                    self.assertLessEqual(load_results["failed_requests"], 0)
                    self.assertLess(load_results["avg_response_time"], 3.0)
                    self.assertLess(load_results["p95_response_time"], 3.0)

    def test_memory_usage_monitoring(self) -> None:
        """Test memory usage during RAG operations."""
        from rag.tests.performance_benchmarks import PerformanceBenchmark

        # Mock external APIs to focus on memory measurement
        mock_query_embedding = [0.1] * 3072
        mock_answer = "Memory management is crucial for system performance."

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
                mock_qdrant.search.return_value = []

                with patch("sentence_transformers.CrossEncoder") as MockCrossEncoder:
                    mock_reranker = MagicMock()
                    MockCrossEncoder.return_value = mock_reranker
                    mock_reranker.predict.return_value = []

                    # Measure memory usage
                    benchmark = PerformanceBenchmark()
                    memory_results = benchmark.measure_memory_usage(
                        rag_service=self.rag_service,
                        query="How is memory managed?",
                        topic_ids=[self.topic.id],
                    )

                    # Verify memory measurement results
                    self.assertIn("peak_memory_mb", memory_results)
                    self.assertIn("memory_delta_mb", memory_results)
                    self.assertIn("baseline_memory_mb", memory_results)

                    # Memory usage should be reasonable
                    self.assertGreater(memory_results["peak_memory_mb"], 0)
                    self.assertGreaterEqual(memory_results["memory_delta_mb"], 0)

    def test_performance_report_generation(self) -> None:
        """Test comprehensive performance report generation."""
        from rag.tests.performance_benchmarks import PerformanceBenchmark

        benchmark = PerformanceBenchmark()

        # Mock benchmark results data
        mock_results = {
            "single_query": {"response_time": 1.5, "success": True},
            "concurrent_queries": {
                "avg_response_time": 2.1,
                "max_response_time": 2.8,
                "success_rate": 1.0,
            },
            "load_test": {
                "avg_response_time": 1.8,
                "p95_response_time": 2.5,
                "p99_response_time": 2.9,
                "requests_per_second": 15.2,
                "success_rate": 0.98,
            },
            "memory_usage": {"peak_memory_mb": 256.7, "memory_delta_mb": 45.3},
        }

        # Generate performance report
        report = benchmark.generate_performance_report(mock_results)

        # Verify report structure
        self.assertIn("summary", report)
        self.assertIn("requirements_met", report)
        self.assertIn("detailed_results", report)
        self.assertIn("recommendations", report)

        # Verify summary metrics
        summary = report["summary"]
        self.assertIn("response_time_requirement_met", summary)
        self.assertIn("overall_performance_score", summary)
        self.assertIn("bottlenecks_identified", summary)

        # Verify requirements assessment
        requirements = report["requirements_met"]
        self.assertIn("three_second_response_time", requirements)
        self.assertIn("concurrent_user_support", requirements)
        self.assertIn("memory_efficiency", requirements)

        # Performance score should be between 0 and 1
        self.assertGreaterEqual(summary["overall_performance_score"], 0.0)
        self.assertLessEqual(summary["overall_performance_score"], 1.0)
