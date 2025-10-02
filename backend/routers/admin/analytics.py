from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import distinct, func
from sqlalchemy.orm import Session

from backend.dependencies.auth import require_admin
from backend.models.base import get_db
from backend.models.history import QuestionHistory
from backend.models.topic import Topic
from backend.models.user import User
from backend.schemas.admin import (
    AnalyticsSummaryOut,
    FeedbackDistributionOut,
    QuestionTrendOut,
    TopicStatsOut,
)

router = APIRouter(prefix="/admin/analytics", tags=["Admin Analytics"])


@router.get("/summary", response_model=AnalyticsSummaryOut)
async def get_analytics_summary(
    db: Annotated[Session, Depends(get_db)],
    _current_admin: Annotated[User, Depends(require_admin)],
) -> AnalyticsSummaryOut:
    total_questions = db.query(func.count(QuestionHistory.id)).scalar() or 0
    total_feedback = (
        db.query(func.count(QuestionHistory.id))
        .filter(QuestionHistory.feedback_score != 0)
        .scalar()
        or 0
    )
    active_sessions = (
        db.query(func.count(distinct(QuestionHistory.session_id))).scalar() or 0
    )
    avg_feedback = (
        db.query(func.avg(QuestionHistory.feedback_score)).scalar() or 0.0
    )

    return AnalyticsSummaryOut(
        total_questions=total_questions,
        total_feedback=total_feedback,
        active_sessions=active_sessions,
        average_feedback_score=float(avg_feedback),
    )


@router.get("/topics", response_model=list[TopicStatsOut])
async def get_topics_stats(
    db: Annotated[Session, Depends(get_db)],
    _current_admin: Annotated[User, Depends(require_admin)],
) -> list[TopicStatsOut]:
    results = (
        db.query(
            Topic.id,
            Topic.name,
            func.count(QuestionHistory.id).label("question_count"),
            func.avg(QuestionHistory.feedback_score).label("avg_feedback"),
        )
        .outerjoin(QuestionHistory, Topic.id == QuestionHistory.topic_id)
        .group_by(Topic.id, Topic.name)
        .all()
    )

    return [
        TopicStatsOut(
            topic_id=row.id,
            topic_name=row.name,
            question_count=row.question_count or 0,
            average_feedback_score=float(row.avg_feedback or 0.0),
        )
        for row in results
    ]


@router.get("/questions/trend", response_model=list[QuestionTrendOut])
async def get_questions_trend(
    db: Annotated[Session, Depends(get_db)],
    _current_admin: Annotated[User, Depends(require_admin)],
    days: Annotated[int, Query(ge=1, le=90)] = 7,
) -> list[QuestionTrendOut]:
    cutoff_date = datetime.now(UTC) - timedelta(days=days)

    results = (
        db.query(
            func.date(QuestionHistory.created_at).label("date"),
            func.count(QuestionHistory.id).label("count"),
        )
        .filter(QuestionHistory.created_at >= cutoff_date)
        .group_by(func.date(QuestionHistory.created_at))
        .order_by(func.date(QuestionHistory.created_at))
        .all()
    )

    return [
        QuestionTrendOut(date=str(row.date), question_count=row.count)
        for row in results
    ]


@router.get("/feedback/distribution", response_model=FeedbackDistributionOut)
async def get_feedback_distribution(
    db: Annotated[Session, Depends(get_db)],
    _current_admin: Annotated[User, Depends(require_admin)],
) -> FeedbackDistributionOut:
    positive = (
        db.query(func.count(QuestionHistory.id))
        .filter(QuestionHistory.feedback_score > 0)
        .scalar()
        or 0
    )
    neutral = (
        db.query(func.count(QuestionHistory.id))
        .filter(QuestionHistory.feedback_score == 0)
        .scalar()
        or 0
    )
    negative = (
        db.query(func.count(QuestionHistory.id))
        .filter(QuestionHistory.feedback_score < 0)
        .scalar()
        or 0
    )

    return FeedbackDistributionOut(
        positive=positive, neutral=neutral, negative=negative
    )
