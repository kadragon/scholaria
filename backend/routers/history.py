"""FastAPI router for question history endpoints (read-only)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.models.base import get_db
from backend.models.history import QuestionHistory
from backend.schemas.history import FeedbackRequest, QuestionHistoryOut

router = APIRouter()


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
