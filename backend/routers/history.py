"""FastAPI router for question history endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.models.base import get_db
from backend.models.history import QuestionHistory
from backend.models.topic import Topic
from backend.schemas.history import (
    FeedbackRequest,
    QuestionHistoryCreate,
    QuestionHistoryOut,
)

router = APIRouter()


@router.post(
    "/history",
    response_model=QuestionHistoryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_history(
    request: QuestionHistoryCreate,
    db: Session = Depends(get_db),
) -> QuestionHistory:
    """Create a new question history record."""
    topic = db.get(Topic, request.topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    history = QuestionHistory(
        topic_id=request.topic_id,
        question=request.question,
        answer=request.answer,
        session_id=request.session_id,
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


@router.get("/history", response_model=list[QuestionHistoryOut])
def list_history(
    topic_id: int = Query(..., description="Topic identifier", ge=1),
    session_id: str | None = Query(
        default=None,
        description="Optional session identifier to filter question history",
        min_length=1,
    ),
    db: Session = Depends(get_db),
) -> list[QuestionHistory]:
    """Return question history filtered by topic and optionally session."""

    query = db.query(QuestionHistory).filter(QuestionHistory.topic_id == topic_id)

    if session_id:
        query = query.filter(QuestionHistory.session_id == session_id)

    histories = query.order_by(QuestionHistory.created_at.desc()).all()
    return histories


@router.patch("/history/{history_id}/feedback", response_model=QuestionHistoryOut)
def update_feedback(
    history_id: int,
    request: FeedbackRequest,
    db: Session = Depends(get_db),
) -> QuestionHistory:
    """Update feedback score for a question history record."""
    history = db.query(QuestionHistory).filter(QuestionHistory.id == history_id).first()

    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History record with id {history_id} not found",
        )

    history.feedback_score = request.feedback_score

    if "feedback_comment" in request.model_fields_set:
        comment = request.feedback_comment
        if comment is not None:
            cleaned = comment.strip()
            history.feedback_comment = cleaned or None
        else:
            history.feedback_comment = None

    db.commit()
    db.refresh(history)
    return history


@router.get("/history/session/{session_id}", response_model=list[QuestionHistoryOut])
def get_session_history(
    session_id: str,
    db: Session = Depends(get_db),
) -> list[QuestionHistory]:
    """Return conversation history for a specific session."""
    histories = (
        db.query(QuestionHistory)
        .filter(QuestionHistory.session_id == session_id)
        .order_by(QuestionHistory.created_at.asc())
        .all()
    )
    return histories
