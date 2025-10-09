"""Integration tests for golden dataset with real Qdrant and Redis."""

from __future__ import annotations

import pytest
import pytest_asyncio

from backend.config import settings
from backend.services.rag_service import AsyncRAGService


@pytest_asyncio.fixture
async def integration_rag_service():
    """Provides AsyncRAGService for integration tests with real services."""
    import redis.asyncio as redis

    redis_client = redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )

    try:
        await redis_client.ping()
    except Exception:
        pytest.skip("Redis not available for integration tests")

    if not settings.OPENAI_API_KEY:
        pytest.skip("OpenAI API key not configured")

    service = AsyncRAGService(
        redis_client=redis_client,
        openai_api_key=settings.OPENAI_API_KEY,
        openai_chat_model=settings.OPENAI_CHAT_MODEL,
        rag_search_limit=10,
        rag_rerank_top_k=5,
    )

    yield service

    await redis_client.close()


def _count_hits(results: list[dict], expected_ids: set[int]) -> int:
    """Count how many expected context IDs appear in results."""
    result_ids = {item["context_item_id"] for item in results}
    return len(result_ids.intersection(expected_ids))


@pytest.mark.integration
@pytest.mark.golden
class TestGoldenDatasetIntegration:
    """Integration tests for golden dataset with real Qdrant vector search."""

    @pytest.mark.asyncio
    async def test_rag_pipeline_with_real_qdrant(
        self, integration_db_with_golden_data, integration_rag_service, golden_dataset
    ):
        """
        RAG pipeline with real Qdrant should achieve >=80% citation accuracy.

        Tests full pipeline: embedding → vector search → reranking → accuracy validation.
        """
        total_hits = 0
        total_expected = 0

        for entry in golden_dataset:
            question = entry["question"]
            topic_id = entry["topic_id"]
            expected_ids = set(entry["expected_context_ids"])

            result = await integration_rag_service.query(
                query=question,
                topic_ids=[topic_id],
                limit=10,
                rerank_top_k=5,
            )

            reranked_results = result.get("context_items", [])

            hits = _count_hits(reranked_results, expected_ids)
            total_hits += hits
            total_expected += len(expected_ids)

            assert hits >= 1, (
                f"No expected contexts found for question: {question}\n"
                f"Expected IDs: {expected_ids}\n"
                f"Got IDs: {[r['context_item_id'] for r in reranked_results]}"
            )

        accuracy = total_hits / total_expected if total_expected else 0.0
        assert accuracy >= 0.8, (
            f"Golden dataset accuracy {accuracy:.2%} below 80% threshold\n"
            f"Total hits: {total_hits}/{total_expected}"
        )

    @pytest.mark.asyncio
    async def test_reranking_improves_accuracy_integration(
        self, integration_db_with_golden_data, golden_dataset
    ):
        """
        Reranking should improve citation accuracy by at least 10% over baseline.

        Compares raw Qdrant search (top-5) vs. BGE reranked (top-5) accuracy.
        """
        from backend.retrieval.embeddings import EmbeddingService
        from backend.retrieval.qdrant import QdrantService
        from backend.retrieval.reranking import RerankingService

        embedding_service = EmbeddingService()
        qdrant_service = QdrantService()
        reranking_service = RerankingService()

        baseline_hits = 0
        reranked_hits = 0
        total_expected = 0

        for entry in golden_dataset:
            question = entry["question"]
            topic_id = entry["topic_id"]
            expected_ids = set(entry["expected_context_ids"])

            query_embedding = embedding_service.generate_embedding(question)

            search_results = qdrant_service.search_similar(
                query_embedding=query_embedding,
                topic_ids=[topic_id],
                limit=10,
            )

            baseline_top_five = search_results[:5]
            reranked_results = reranking_service.rerank_results(
                query=question,
                search_results=search_results,
                top_k=5,
            )

            baseline_hits += _count_hits(baseline_top_five, expected_ids)
            reranked_hits += _count_hits(reranked_results, expected_ids)
            total_expected += len(expected_ids)

        assert total_expected > 0, "Golden dataset must include expected context IDs"

        baseline_accuracy = baseline_hits / total_expected
        reranked_accuracy = reranked_hits / total_expected

        assert reranked_accuracy >= baseline_accuracy, (
            f"Reranked accuracy {reranked_accuracy:.2%} should not be lower than "
            f"baseline {baseline_accuracy:.2%}"
        )

        improvement = reranked_accuracy - baseline_accuracy
        if baseline_accuracy < 1.0:
            assert improvement >= 0.1, (
                f"Reranking should improve accuracy by at least 10% when baseline < 100%\n"
                f"Baseline: {baseline_accuracy:.2%}, Reranked: {reranked_accuracy:.2%}\n"
                f"Improvement: {improvement:.2%}"
            )
