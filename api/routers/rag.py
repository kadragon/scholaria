"""
FastAPI router for RAG question-answer endpoints.
"""

import logging
from typing import Annotated

import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies.redis import get_redis
from api.schemas.rag import AnswerResponse, QuestionRequest
from api.services.rag_service import AsyncRAGService

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_rag_service(
    redis_client: Annotated[redis.Redis, Depends(get_redis)],
) -> AsyncRAGService:
    """
    Get RAG service instance with dependencies injected.

    Args:
        redis_client: Redis client for caching

    Returns:
        AsyncRAGService instance
    """
    import os

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key not configured",
        )

    return AsyncRAGService(
        redis_client=redis_client,
        openai_api_key=openai_api_key,
        openai_chat_model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        openai_chat_temperature=float(os.getenv("OPENAI_CHAT_TEMPERATURE", "0.3")),
        openai_chat_max_tokens=int(os.getenv("OPENAI_CHAT_MAX_TOKENS", "1000")),
        rag_search_limit=int(os.getenv("RAG_SEARCH_LIMIT", "10")),
        rag_rerank_top_k=int(os.getenv("RAG_RERANK_TOP_K", "5")),
    )


@router.post("/rag/ask", response_model=AnswerResponse)
async def ask_question(
    request: QuestionRequest,
    rag_service: Annotated[AsyncRAGService, Depends(get_rag_service)],
) -> AnswerResponse:
    """
    Process a question and return an answer with citations.

    Args:
        request: Question request with topic_id and question
        rag_service: RAG service instance

    Returns:
        Answer with citations and topic_id

    Raises:
        HTTPException: 400 for validation errors, 503 for service errors, 500 for internal errors
    """
    try:
        result = await rag_service.query(
            query=request.question,
            topic_ids=[request.topic_id],
        )

        # Format citations from sources
        from api.schemas.rag import Citation

        citations = [
            Citation(
                title=source["title"],
                content=source["content"][:200] + "..."
                if len(source["content"]) > 200
                else source["content"],
                score=source["score"],
                context_type=source["context_type"],
                context_item_id=source["context_item_id"],
            )
            for source in result["sources"]
        ]

        return AnswerResponse(
            answer=result["answer"],
            citations=citations,
            topic_id=request.topic_id,
        )

    except ValueError as e:
        # Handle validation errors from RAG service
        logger.warning("RAG validation error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request parameters.",
        ) from e

    except ConnectionError as e:
        # Handle external service connection errors
        logger.error("RAG connection error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to connect to external services. Please try again later.",
        ) from e

    except Exception as e:
        # Log the error for debugging
        logger.error("RAG pipeline error: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your question. Please try again.",
        ) from e
