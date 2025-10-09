from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, distinct, func
from sqlalchemy.orm import Session

from backend.dependencies.auth import require_admin
from backend.models.base import get_db
from backend.models.history import QuestionHistory
from backend.models.topic import Topic
from backend.models.user import User
from backend.schemas.admin import (
    AnalyticsSummaryOut,
    FeedbackCommentOut,
    FeedbackDistributionOut,
    QuestionTrendOut,
    TopicStatsOut,
)

router = APIRouter(prefix="/analytics", tags=["Admin Analytics"])


@router.get("/summary", response_model=AnalyticsSummaryOut)
async def get_analytics_summary(
    db: Annotated[Session, Depends(get_db)],
    _current_admin: Annotated[User, Depends(require_admin)],
) -> AnalyticsSummaryOut:
    results = db.query(
        func.count(QuestionHistory.id),
        func.count(func.nullif(QuestionHistory.feedback_score, 0)),
        func.count(distinct(QuestionHistory.session_id)),
        func.avg(QuestionHistory.feedback_score),
    ).one()

    total_questions = results[0] or 0
    total_feedback = results[1] or 0
    active_sessions = results[2] or 0
    avg_feedback = results[3] or 0.0

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
    results = db.query(
        func.sum(case((QuestionHistory.feedback_score > 0, 1), else_=0)).label(
            "positive"
        ),
        func.sum(case((QuestionHistory.feedback_score == 0, 1), else_=0)).label(
            "neutral"
        ),
        func.sum(case((QuestionHistory.feedback_score < 0, 1), else_=0)).label(
            "negative"
        ),
    ).one()

    positive = results.positive or 0
    neutral = results.neutral or 0
    negative = results.negative or 0

    return FeedbackDistributionOut(
        positive=positive, neutral=neutral, negative=negative
    )


@router.get("/feedback/comments", response_model=list[FeedbackCommentOut])
async def get_feedback_comments(
    db: Annotated[Session, Depends(get_db)],
    _current_admin: Annotated[User, Depends(require_admin)],
    topic_id: Annotated[int | None, Query(ge=1)] = None,
    limit: Annotated[int, Query(gt=0, le=100)] = 20,
) -> list[FeedbackCommentOut]:
    query = (
        db.query(
            QuestionHistory.id.label("history_id"),
            Topic.id.label("topic_id"),
            Topic.name.label("topic_name"),
            QuestionHistory.feedback_score,
            QuestionHistory.feedback_comment,
            QuestionHistory.created_at,
        )
        .join(Topic, Topic.id == QuestionHistory.topic_id)
        .filter(QuestionHistory.feedback_comment.isnot(None))
        .filter(func.trim(QuestionHistory.feedback_comment) != "")
        .order_by(QuestionHistory.created_at.desc())
    )

    if topic_id is not None:
        query = query.filter(QuestionHistory.topic_id == topic_id)

    results = query.limit(limit).all()

    return [
        FeedbackCommentOut(
            history_id=row.history_id,
            topic_id=row.topic_id,
            topic_name=row.topic_name,
            feedback_score=row.feedback_score,
            feedback_comment=row.feedback_comment,
            created_at=row.created_at,
        )
        for row in results
    ]
