"""
FastAPI router for Topic resource.

POC implementation - GET /api/topics endpoint.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, selectinload

from backend.models.base import get_db
from backend.models.topic import Topic
from backend.schemas.topic import TopicOut

router = APIRouter()


@router.get("/topics", response_model=list[TopicOut])
def list_topics(db: Session = Depends(get_db)) -> list[Topic]:
    """
    List all topics.

    Equivalent to Django rag.views.TopicListView.
    """
    topics = (
        db.query(Topic).options(selectinload(Topic.contexts)).order_by(Topic.name).all()
    )
    return topics


@router.get("/topics/slug/{slug}", response_model=TopicOut)
def get_topic_by_slug(slug: str, db: Session = Depends(get_db)) -> Topic:
    """
    Get a single topic by slug.
    """
    topic = (
        db.query(Topic)
        .options(selectinload(Topic.contexts))
        .filter(Topic.slug == slug)
        .first()
    )
    if not topic:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


@router.get("/topics/{topic_id}", response_model=TopicOut)
def get_topic(topic_id: int, db: Session = Depends(get_db)) -> Topic:
    """
    Get a single topic by ID.

    Equivalent to Django rag.views.TopicDetailView.
    """
    topic = (
        db.query(Topic)
        .options(selectinload(Topic.contexts))
        .filter(Topic.id == topic_id)
        .first()
    )
    if not topic:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Topic not found")
    return topic
