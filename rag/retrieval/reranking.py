from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sentence_transformers import CrossEncoder

if TYPE_CHECKING:
    pass


class RerankingService:
    """Service for reranking search results using BGE reranker."""

    def __init__(self) -> None:
        self.model = CrossEncoder("BAAI/bge-reranker-base")

    def rerank_results(
        self,
        query: str | None,
        search_results: list[dict[str, Any]],
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Rerank search results using BGE reranker model.

        Args:
            query: Query string to rank against
            search_results: List of search results to rerank
            top_k: Maximum number of results to return

        Returns:
            Reranked results sorted by relevance score (descending)

        Raises:
            ValueError: If query is None/empty or search_results is empty
        """
        if query is None or not query.strip():
            raise ValueError("Query cannot be None or empty")

        if not search_results:
            raise ValueError("Search results cannot be empty")

        # Prepare input pairs for the cross-encoder
        input_pairs = [(query, result["content"]) for result in search_results]

        # Get reranking scores
        rerank_scores = self.model.predict(input_pairs)

        # Add rerank scores to results and sort
        reranked_results = []
        for i, result in enumerate(search_results):
            result_with_score = result.copy()
            result_with_score["rerank_score"] = float(rerank_scores[i])
            reranked_results.append(result_with_score)

        # Sort by rerank score (descending)
        reranked_results.sort(key=lambda x: x["rerank_score"], reverse=True)

        # Apply top_k limitation if specified
        if top_k is not None:
            reranked_results = reranked_results[:top_k]

        return reranked_results
