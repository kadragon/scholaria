"""Contexts Admin API for Refine Admin Panel."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.dependencies.auth import require_admin
from backend.models.base import get_db
from backend.models.context import Context
from backend.models.user import User
from backend.schemas.admin import (
    AdminContextCreate,
    AdminContextOut,
    AdminContextUpdate,
    ContextListResponse,
)

router = APIRouter(prefix="/contexts", tags=["Admin - Contexts"])


@router.get("/", response_model=ContextListResponse)
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

    contexts_out = []
    for ctx in contexts:
        contexts_out.append(
            AdminContextOut(
                id=ctx.id,
                name=ctx.name,
                description=ctx.description,
                context_type=ctx.context_type,
                chunk_count=ctx.chunk_count,
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

    return AdminContextOut(
        id=ctx.id,
        name=ctx.name,
        description=ctx.description,
        context_type=ctx.context_type,
        chunk_count=ctx.chunk_count,
        processing_status=ctx.processing_status,
        topics_count=len(ctx.topics),
        created_at=ctx.created_at,
        updated_at=ctx.updated_at,
    )


@router.post("/", response_model=AdminContextOut, status_code=status.HTTP_201_CREATED)
async def create_context(
    context_data: AdminContextCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> AdminContextOut:
    """Create a new context."""
    ctx = Context(
        name=context_data.name,
        description=context_data.description,
        context_type=context_data.context_type,
        original_content=context_data.original_content,
    )
    db.add(ctx)
    db.commit()
    db.refresh(ctx)

    return AdminContextOut(
        id=ctx.id,
        name=ctx.name,
        description=ctx.description,
        context_type=ctx.context_type,
        chunk_count=ctx.chunk_count,
        processing_status=ctx.processing_status,
        topics_count=len(ctx.topics),
        created_at=ctx.created_at,
        updated_at=ctx.updated_at,
    )


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
        from backend.models.topic import Topic

        topics = db.query(Topic).filter(Topic.id.in_(context_data.topic_ids)).all()
        ctx.topics = topics

    db.commit()
    db.refresh(ctx)

    return AdminContextOut(
        id=ctx.id,
        name=ctx.name,
        description=ctx.description,
        context_type=ctx.context_type,
        chunk_count=ctx.chunk_count,
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
