"""FastAPI router for RAG streaming endpoints."""

import logging
from collections.abc import AsyncGenerator
from typing import Annotated

import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, status
from sse_starlette.sse import EventSourceResponse

from backend.config import settings
from backend.dependencies.redis import get_redis
from backend.schemas.rag import StreamQuestionRequest
from backend.services.rag_service import AsyncRAGService

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_rag_service(
    redis_client: Annotated[redis.Redis, Depends(get_redis)],
) -> AsyncRAGService:
    """Get RAG service instance with dependencies injected."""
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key not configured",
        )

    return AsyncRAGService(
        redis_client=redis_client,
        openai_api_key=settings.OPENAI_API_KEY,
        openai_chat_model=settings.OPENAI_CHAT_MODEL,
        openai_chat_temperature=settings.OPENAI_CHAT_TEMPERATURE,
        openai_chat_max_tokens=settings.OPENAI_CHAT_MAX_TOKENS,
        rag_search_limit=settings.RAG_SEARCH_LIMIT,
        rag_rerank_top_k=settings.RAG_RERANK_TOP_K,
    )


@router.post("/rag/stream")
async def stream_answer(
    request: StreamQuestionRequest,
    rag_service: Annotated[AsyncRAGService, Depends(get_rag_service)],
) -> EventSourceResponse:
    """Stream RAG answer with Server-Sent Events."""

    async def event_generator() -> AsyncGenerator[dict[str, str]]:
        try:
            async for event_data in rag_service.query_stream(
                query=request.question,
                topic_ids=[request.topic_id],
            ):
                yield {"data": event_data}
        except Exception as e:
            logger.error("Streaming error: %s", str(e), exc_info=True)
            yield {"data": '{"type": "error", "message": "Internal server error"}'}

    return EventSourceResponse(event_generator())
