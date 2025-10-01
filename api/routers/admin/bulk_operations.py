"""Bulk operations endpoints for Admin API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.dependencies.auth import require_admin
from api.models.base import get_db
from api.models.context import Context
from api.models.topic import Topic
from api.models.user import User
from api.schemas.admin import (
    BulkAssignContextRequest,
    BulkAssignContextResponse,
    BulkRegenerateEmbeddingsRequest,
    BulkRegenerateEmbeddingsResponse,
    BulkUpdateSystemPromptRequest,
    BulkUpdateSystemPromptResponse,
)
from core.celery import app as celery_app

router = APIRouter(prefix="/bulk", tags=["admin-bulk"])


@router.post(
    "/assign-context-to-topic",
    response_model=BulkAssignContextResponse,
    status_code=status.HTTP_200_OK,
)
async def bulk_assign_context_to_topic(
    request: BulkAssignContextRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> BulkAssignContextResponse:
    """Bulk assign contexts to a topic."""
    topic = db.scalar(select(Topic).where(Topic.id == request.topic_id))
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic with id {request.topic_id} not found",
        )

    contexts = db.scalars(
        select(Context).where(Context.id.in_(request.context_ids))
    ).all()

    if len(contexts) != len(request.context_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more context IDs not found",
        )

    for context in contexts:
        if context not in topic.contexts:
            topic.contexts.append(context)

    db.commit()

    return BulkAssignContextResponse(assigned_count=len(contexts), topic_id=topic.id)


@router.post(
    "/regenerate-embeddings",
    response_model=BulkRegenerateEmbeddingsResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def bulk_regenerate_embeddings(
    request: BulkRegenerateEmbeddingsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> BulkRegenerateEmbeddingsResponse:
    """Bulk regenerate embeddings for contexts (queues Celery tasks)."""
    contexts = db.scalars(
        select(Context).where(Context.id.in_(request.context_ids))
    ).all()

    if len(contexts) != len(request.context_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more context IDs not found",
        )

    task_ids = []
    for context in contexts:
        context.processing_status = "PENDING"

        task = celery_app.send_task(
            "rag.tasks.regenerate_embeddings_for_context",
            args=[context.id],
        )
        task_ids.append(str(task.id))

    db.commit()

    return BulkRegenerateEmbeddingsResponse(
        queued_count=len(task_ids), task_ids=task_ids
    )


@router.post(
    "/update-system-prompt",
    response_model=BulkUpdateSystemPromptResponse,
    status_code=status.HTTP_200_OK,
)
async def bulk_update_system_prompt(
    request: BulkUpdateSystemPromptRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> BulkUpdateSystemPromptResponse:
    """Bulk update system prompts for topics."""
    topics = db.scalars(select(Topic).where(Topic.id.in_(request.topic_ids))).all()

    if len(topics) != len(request.topic_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more topic IDs not found",
        )

    for topic in topics:
        topic.system_prompt = request.system_prompt

    db.commit()

    return BulkUpdateSystemPromptResponse(updated_count=len(topics))
