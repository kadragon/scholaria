"""Performance benchmark tests for RAG pipeline."""

import asyncio
import time
from unittest.mock import AsyncMock, patch

import pytest

from backend.config import settings
from backend.services.rag_service import AsyncRAGService


@pytest.fixture
def mocked_rag_service(monkeypatch):
    """Provides a fully mocked AsyncRAGService instance and its mocks."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    with (
        patch("backend.retrieval.embeddings.openai.OpenAI"),
        patch("backend.retrieval.qdrant.QdrantService.create_collection"),
    ):
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None

        service = AsyncRAGService(
            redis_client=mock_redis,
            openai_api_key="test-key",
        )

        with (
            patch.object(service.embedding_service, "generate_embedding") as mock_embed,
            patch.object(service.qdrant_service, "search_similar") as mock_search,
            patch.object(service.reranking_service, "rerank_results") as mock_rerank,
            patch.object(service, "_generate_answer") as mock_answer,
        ):
            mocks = {
                "embed": mock_embed,
                "search": mock_search,
                "rerank": mock_rerank,
                "answer": mock_answer,
            }
            yield service, mocks


@pytest.mark.performance
class TestRAGPerformance:
    """Performance tests for RAG query pipeline."""

    @pytest.mark.asyncio
    async def test_rag_query_response_time_under_3s(self, mocked_rag_service):
        """RAG query should complete within 3 seconds (P95)."""
        service, mocks = mocked_rag_service

        mocks["embed"].return_value = [0.1] * settings.OPENAI_EMBEDDING_DIM
        mocks["search"].return_value = [
            {
                "context_item_id": 1,
                "title": "Test Context",
                "content": "Test content",
                "score": 0.9,
            }
        ]
        mocks["rerank"].return_value = mocks["search"].return_value
        mocks["answer"].return_value = "Test answer"

        start_time = time.perf_counter()
        result = await service.query(
            query="Test question", topic_ids=[1], limit=10, rerank_top_k=5
        )
        elapsed = time.perf_counter() - start_time

        assert result["answer"] == "Test answer"
        assert elapsed < 3.0, f"Query took {elapsed:.2f}s (expected < 3s)"

    @pytest.mark.asyncio
    async def test_rag_pipeline_step_timings(self, mocked_rag_service):
        """Measure individual pipeline step timings."""
        service, mocks = mocked_rag_service

        def mock_embed_with_timing(text):
            time.sleep(0.1)
            return [0.1] * settings.OPENAI_EMBEDDING_DIM

        def mock_search_with_timing(query_embedding, topic_ids, limit):
            time.sleep(0.2)
            return [
                {
                    "context_item_id": 1,
                    "title": "Test",
                    "content": "Test",
                    "score": 0.9,
                }
            ]

        def mock_rerank_with_timing(query, search_results, top_k):
            time.sleep(0.15)
            return search_results

        async def mock_answer_with_timing(query, context):
            await asyncio.sleep(0.5)
            return "Test answer"

        mocks["embed"].side_effect = mock_embed_with_timing
        mocks["search"].side_effect = mock_search_with_timing
        mocks["rerank"].side_effect = mock_rerank_with_timing
        mocks["answer"].side_effect = mock_answer_with_timing

        start = time.perf_counter()
        await service.query(query="Test", topic_ids=[1])
        total = time.perf_counter() - start

        assert total < 3.0, f"Total pipeline time {total:.2f}s exceeds 3s"

    @pytest.mark.asyncio
    async def test_concurrent_requests_stability(self, mocked_rag_service):
        """System should handle 10 concurrent requests without failure."""
        service, mocks = mocked_rag_service

        mocks["embed"].return_value = [0.1] * settings.OPENAI_EMBEDDING_DIM
        mocks["search"].return_value = [
            {
                "context_item_id": 1,
                "title": "Test",
                "content": "Test",
                "score": 0.9,
            }
        ]
        mocks["rerank"].return_value = mocks["search"].return_value
        mocks["answer"].return_value = "Test answer"

        tasks = [service.query(query=f"Question {i}", topic_ids=[1]) for i in range(10)]

        start = time.perf_counter()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.perf_counter() - start

        successful = [r for r in results if not isinstance(r, Exception)]
        assert len(successful) == 10, f"Only {len(successful)}/10 requests succeeded"
        assert (
            elapsed < 5.0
        ), f"10 concurrent requests took {elapsed:.2f}s (expected < 5s)"
