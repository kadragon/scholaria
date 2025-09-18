from __future__ import annotations

from typing import TYPE_CHECKING, Any

from openai import OpenAI

from .embeddings import EmbeddingService
from .qdrant import QdrantService
from .reranking import RerankingService

if TYPE_CHECKING:
    pass


class RAGService:
    """Complete RAG query pipeline service."""

    def __init__(self) -> None:
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()
        self.reranking_service = RerankingService()
        self.openai_client = OpenAI()

    def query(
        self,
        query: str | None,
        topic_ids: list[int],
        limit: int = 10,
        rerank_top_k: int = 5,
    ) -> dict[str, Any]:
        """
        Execute a complete RAG query pipeline.

        Args:
            query: User's question
            topic_ids: List of topic IDs to search within
            limit: Maximum number of initial search results
            rerank_top_k: Maximum number of results after reranking

        Returns:
            Dictionary containing answer, sources, and context items

        Raises:
            ValueError: If query is None/empty or topic_ids is empty
        """
        if query is None or not query.strip():
            raise ValueError("Query cannot be None or empty")

        if not topic_ids:
            raise ValueError("Topic IDs cannot be empty")

        # Step 1: Generate embedding for the query
        query_embedding = self.embedding_service.generate_embedding(query)

        # Step 2: Search for similar context items in Qdrant
        search_results = self.qdrant_service.search_similar(
            query_embedding=query_embedding, topic_ids=topic_ids, limit=limit
        )

        # If no results found, return empty response
        if not search_results:
            return {
                "answer": "I couldn't find any relevant information for your question in the selected topics.",
                "sources": [],
                "context_items": [],
            }

        # Step 3: Rerank results using BGE reranker
        reranked_results = self.reranking_service.rerank_results(
            query=query, search_results=search_results, top_k=rerank_top_k
        )

        # Step 4: Prepare context for the LLM
        context_text = self._prepare_context(reranked_results)

        # Step 5: Generate answer using OpenAI
        answer = self._generate_answer(query, context_text)

        # Step 6: Format response
        sources = [
            {
                "title": result["title"],
                "content": result["content"],
                "score": result.get("rerank_score", result.get("score", 0.0)),
                "context_type": result.get("context_type", ""),
                "context_item_id": result["context_item_id"],
            }
            for result in reranked_results
        ]

        return {"answer": answer, "sources": sources, "context_items": reranked_results}

    def _prepare_context(self, search_results: list[dict[str, Any]]) -> str:
        """
        Prepare context text from search results for the LLM.

        Args:
            search_results: List of search results with content

        Returns:
            Formatted context text
        """
        if not search_results:
            return ""

        context_parts = []
        for i, result in enumerate(search_results, 1):
            context_parts.append(
                f"[Source {i}] {result['title']}\n{result['content']}\n"
            )

        return "\n".join(context_parts)

    def _generate_answer(self, query: str, context: str) -> str:
        """
        Generate an answer using OpenAI API.

        Args:
            query: User's question
            context: Context information from search results

        Returns:
            Generated answer
        """
        if not context:
            return "I couldn't find any relevant information to answer your question."

        # Create the prompt
        prompt = f"""You are a helpful assistant that answers questions based on the provided context.

Context:
{context}

Question: {query}

Please provide a comprehensive answer based on the context above. If the context doesn't contain enough information to fully answer the question, acknowledge this in your response. Include relevant details from the sources where appropriate."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides accurate answers based on the given context.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1000,
        )

        return (
            response.choices[0].message.content
            or "I apologize, but I couldn't generate an answer at this time."
        )
