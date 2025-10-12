"""Contexts Admin API for Refine Admin Panel."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.dependencies.auth import require_admin
from backend.models.base import get_db
from backend.models.context import Context, ContextItem
from backend.models.topic import Topic
from backend.models.user import User
from backend.schemas.admin import (
    AdminContextItemUpdate,
    AdminContextOut,
    AdminContextUpdate,
    AdminFaqQaCreate,
    ContextListResponse,
    ProcessingStatusResponse,
)
from backend.schemas.context import ContextItemOut
from backend.tasks.embeddings import regenerate_embedding_task

router = APIRouter(prefix="/contexts", tags=["Admin - Contexts"])


@router.get("", response_model=ContextListResponse)
async def list_contexts(
    skip: int = 0,
    limit: int = 10,
    sort: str | None = None,
    filter: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> ContextListResponse:
    """List all contexts with pagination, filtering, and sorting (Refine format)."""
    query = db.query(Context)

    # Apply filters
    if filter:
        try:
            filters = json.loads(filter)
            if "context_type" in filters:
                query = query.filter(Context.context_type == filters["context_type"])
            if "name" in filters:
                query = query.filter(Context.name.ilike(f"%{filters['name']}%"))
        except json.JSONDecodeError:
            pass

    # Apply sorting
    if sort:
        parts = sort.rsplit("_", 1)
        if len(parts) == 2:
            field, order = parts
            if hasattr(Context, field):
                column = getattr(Context, field)
                if order == "desc":
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column)

    total = query.count()
    contexts = query.offset(skip).limit(limit).all()

    context_ids = [ctx.id for ctx in contexts]
    chunk_counts_raw = (
        db.query(ContextItem.context_id, func.count(ContextItem.id))
        .filter(ContextItem.context_id.in_(context_ids))
        .group_by(ContextItem.context_id)
        .all()
    )
    chunk_count_map: dict[int, int] = {
        ctx_id: int(count) for ctx_id, count in chunk_counts_raw
    }

    contexts_out = []
    for ctx in contexts:
        contexts_out.append(
            AdminContextOut(
                id=ctx.id,
                name=ctx.name,
                description=ctx.description,
                context_type=ctx.context_type,
                chunk_count=chunk_count_map.get(ctx.id, 0),
                processing_status=ctx.processing_status,
                topics_count=len(ctx.topics),
                created_at=ctx.created_at,
                updated_at=ctx.updated_at,
            )
        )

    return ContextListResponse(data=contexts_out, total=total)


@router.get("/{id}", response_model=AdminContextOut)
async def get_context(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> AdminContextOut:
    """Get a single context by ID."""
    ctx = db.query(Context).filter(Context.id == id).first()
    if not ctx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Context not found"
        )

    actual_chunk_count = (
        db.query(ContextItem).filter(ContextItem.context_id == ctx.id).count()
    )

    return AdminContextOut(
        id=ctx.id,
        name=ctx.name,
        description=ctx.description,
        context_type=ctx.context_type,
        chunk_count=actual_chunk_count,
        processing_status=ctx.processing_status,
        topics_count=len(ctx.topics),
        created_at=ctx.created_at,
        updated_at=ctx.updated_at,
    )


@router.post("", response_model=AdminContextOut, status_code=status.HTTP_201_CREATED)
async def create_context(
    name: str = Form(...),
    description: str = Form(...),
    context_type: str = Form(...),
    original_content: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> AdminContextOut:
    """Create a new context."""
    processing_status = "COMPLETED" if context_type == "FAQ" else "PENDING"

    ctx = Context(
        name=name,
        description=description,
        context_type=context_type,
        original_content=original_content,
        processing_status=processing_status,
    )
    db.add(ctx)
    db.commit()
    db.refresh(ctx)

    actual_chunk_count = 0

    return AdminContextOut(
        id=ctx.id,
        name=ctx.name,
        description=ctx.description,
        context_type=ctx.context_type,
        chunk_count=actual_chunk_count,
        processing_status=ctx.processing_status,
        topics_count=len(ctx.topics),
        created_at=ctx.created_at,
        updated_at=ctx.updated_at,
    )


@router.patch("/{id}", response_model=AdminContextOut)
@router.put("/{id}", response_model=AdminContextOut)
async def update_context(
    id: int,
    context_data: AdminContextUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> AdminContextOut:
    """Update an existing context."""
    ctx = db.query(Context).filter(Context.id == id).first()
    if not ctx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Context not found"
        )

    if context_data.name is not None:
        ctx.name = context_data.name
    if context_data.description is not None:
        ctx.description = context_data.description
    if context_data.original_content is not None:
        ctx.original_content = context_data.original_content

    if context_data.topic_ids is not None:
        topics = db.query(Topic).filter(Topic.id.in_(context_data.topic_ids)).all()
        ctx.topics = topics

    db.commit()
    db.refresh(ctx)

    actual_chunk_count = (
        db.query(ContextItem).filter(ContextItem.context_id == ctx.id).count()
    )

    return AdminContextOut(
        id=ctx.id,
        name=ctx.name,
        description=ctx.description,
        context_type=ctx.context_type,
        chunk_count=actual_chunk_count,
        processing_status=ctx.processing_status,
        topics_count=len(ctx.topics),
        created_at=ctx.created_at,
        updated_at=ctx.updated_at,
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_context(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> None:
    """Delete a context."""
    ctx = db.query(Context).filter(Context.id == id).first()
    if not ctx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Context not found"
        )

    db.delete(ctx)
    db.commit()


@router.get("/{id}/items", response_model=list[ContextItemOut])
async def get_context_items(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> list[ContextItem]:
    """Get all items for a specific context."""
    ctx = db.query(Context).filter(Context.id == id).first()
    if not ctx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Context not found"
        )

    items = db.query(ContextItem).filter(ContextItem.context_id == id).all()
    return items


@router.post(
    "/{id}/qa", response_model=ContextItemOut, status_code=status.HTTP_201_CREATED
)
async def add_faq_qa(
    id: int,
    qa_data: AdminFaqQaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> ContextItem:
    """Add a Q&A pair to a FAQ context."""
    ctx = db.query(Context).filter(Context.id == id).first()
    if not ctx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Context not found"
        )

    if ctx.context_type != "FAQ":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only add Q&A pairs to FAQ contexts.",
        )

    qa_item = ContextItem(
        title=qa_data.title,
        content=qa_data.content,
        context_id=ctx.id,
    )
    db.add(qa_item)

    db.commit()
    db.refresh(qa_item)

    return qa_item


@router.patch("/{context_id}/items/{item_id}", response_model=ContextItemOut)
async def update_context_item(
    context_id: int,
    item_id: int,
    update_data: AdminContextItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> ContextItem:
    """Update a context item."""
    ctx = db.query(Context).filter(Context.id == context_id).first()
    if not ctx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Context not found"
        )

    item = (
        db.query(ContextItem)
        .filter(ContextItem.id == item_id, ContextItem.context_id == context_id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Context item not found"
        )

    if update_data.content is not None:
        item.content = update_data.content

    if update_data.order_index is not None:
        item.order_index = update_data.order_index

    db.commit()
    db.refresh(item)

    if update_data.content is not None:
        regenerate_embedding_task.delay(item.id)

    return item


@router.get("/{id}/processing-status", response_model=ProcessingStatusResponse)
async def get_context_processing_status(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> ProcessingStatusResponse:
    """Get processing status for a context."""
    ctx = db.query(Context).filter(Context.id == id).first()
    if not ctx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Context not found"
        )

    # Calculate progress based on processing status
    if ctx.processing_status == "COMPLETED":
        progress = 100
    elif ctx.processing_status == "FAILED":
        progress = 0
    elif ctx.processing_status == "PROCESSING":
        # For simplicity, assume 50% progress when processing
        # In a real implementation, you might track actual progress
        progress = 50
    else:  # PENDING
        progress = 0

    return ProcessingStatusResponse(status=ctx.processing_status, progress=progress)
