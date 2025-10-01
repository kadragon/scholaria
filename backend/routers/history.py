"""FastAPI router for question history endpoints (read-only)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.models.base import get_db
from backend.models.history import QuestionHistory
from backend.schemas.history import QuestionHistoryOut

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
