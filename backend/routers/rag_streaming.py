"""FastAPI router for RAG streaming endpoints."""

import logging
from typing import Annotated, Any

import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, status
from sse_starlette.sse import EventSourceResponse

from backend.dependencies.redis import get_redis
from backend.schemas.rag import StreamQuestionRequest
from backend.services.rag_service import AsyncRAGService

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_rag_service(
    redis_client: Annotated[redis.Redis, Depends(get_redis)],
) -> AsyncRAGService:
    """Get RAG service instance with dependencies injected."""
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


@router.post("/rag/stream")
async def stream_answer(
    request: StreamQuestionRequest,
    rag_service: Annotated[AsyncRAGService, Depends(get_rag_service)],
) -> EventSourceResponse:
    """Stream RAG answer with Server-Sent Events."""

    async def event_generator() -> Any:
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
