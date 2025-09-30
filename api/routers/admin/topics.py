"""Topics Admin API for Refine Admin Panel."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies.auth import require_admin
from api.models.base import get_db
from api.models.context import Context
from api.models.topic import Topic
from api.models.user import User
from api.schemas.admin import (
    AdminTopicCreate,
    AdminTopicOut,
    AdminTopicUpdate,
    TopicListResponse,
)

router = APIRouter(prefix="/topics", tags=["Admin - Topics"])


@router.get("/", response_model=TopicListResponse)
async def list_topics(
    skip: int = 0,
    limit: int = 10,
    sort: str | None = None,
    filter: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> TopicListResponse:
    """List all topics with pagination, filtering, and sorting (Refine format)."""
    query = db.query(Topic)

    # Apply filters
    if filter:
        try:
            filters = json.loads(filter)
            if "name" in filters:
                query = query.filter(Topic.name.ilike(f"%{filters['name']}%"))
            if "description" in filters:
                query = query.filter(
                    Topic.description.ilike(f"%{filters['description']}%")
                )
        except json.JSONDecodeError:
            pass

    # Apply sorting
    if sort:
        parts = sort.rsplit("_", 1)
        if len(parts) == 2:
            field, order = parts
            if hasattr(Topic, field):
                column = getattr(Topic, field)
                if order == "desc":
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column)

    total = query.count()
    topics = query.offset(skip).limit(limit).all()

    # Add contexts_count to each topic
    topics_out = []
    for topic in topics:
        topic_dict = {
            "id": topic.id,
            "name": topic.name,
            "description": topic.description,
            "system_prompt": topic.system_prompt or "",
            "contexts_count": len(topic.contexts),
            "created_at": topic.created_at,
            "updated_at": topic.updated_at,
        }
        topics_out.append(AdminTopicOut.model_validate(topic_dict))

    return TopicListResponse(data=topics_out, total=total)


@router.get("/{id}", response_model=AdminTopicOut)
async def get_topic(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> AdminTopicOut:
    """Get a single topic by ID."""
    topic = db.query(Topic).filter(Topic.id == id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found"
        )

    return AdminTopicOut(
        id=topic.id,
        name=topic.name,
        description=topic.description,
        system_prompt=topic.system_prompt or "",
        contexts_count=len(topic.contexts),
        created_at=topic.created_at,
        updated_at=topic.updated_at,
    )


@router.post("/", response_model=AdminTopicOut, status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic_data: AdminTopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> AdminTopicOut:
    """Create a new topic with optional context associations."""
    # Create topic
    topic = Topic(
        name=topic_data.name,
        description=topic_data.description,
        system_prompt=topic_data.system_prompt,
    )

    # Associate contexts if provided
    if topic_data.context_ids:
        contexts = (
            db.query(Context).filter(Context.id.in_(topic_data.context_ids)).all()
        )
        topic.contexts = contexts

    db.add(topic)
    db.commit()
    db.refresh(topic)

    return AdminTopicOut(
        id=topic.id,
        name=topic.name,
        description=topic.description,
        system_prompt=topic.system_prompt or "",
        contexts_count=len(topic.contexts),
        created_at=topic.created_at,
        updated_at=topic.updated_at,
    )


@router.put("/{id}", response_model=AdminTopicOut)
async def update_topic(
    id: int,
    topic_data: AdminTopicUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> AdminTopicOut:
    """Update an existing topic."""
    topic = db.query(Topic).filter(Topic.id == id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found"
        )

    # Update fields
    if topic_data.name is not None:
        topic.name = topic_data.name
    if topic_data.description is not None:
        topic.description = topic_data.description
    if topic_data.system_prompt is not None:
        topic.system_prompt = topic_data.system_prompt

    # Update context associations
    if topic_data.context_ids is not None:
        contexts = (
            db.query(Context).filter(Context.id.in_(topic_data.context_ids)).all()
        )
        topic.contexts = contexts

    db.commit()
    db.refresh(topic)

    return AdminTopicOut(
        id=topic.id,
        name=topic.name,
        description=topic.description,
        system_prompt=topic.system_prompt or "",
        contexts_count=len(topic.contexts),
        created_at=topic.created_at,
        updated_at=topic.updated_at,
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> None:
    """Delete a topic."""
    topic = db.query(Topic).filter(Topic.id == id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found"
        )

    db.delete(topic)
    db.commit()
