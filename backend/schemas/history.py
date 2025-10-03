"""Pydantic schemas for question history endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from backend.schemas.utils import to_local_iso


class FeedbackRequest(BaseModel):
    """Request schema for updating feedback score."""

    feedback_score: int = Field(
        ..., ge=-1, le=1, description="Feedback: -1 (dislike), 0 (neutral), 1 (like)"
    )


class QuestionHistoryOut(BaseModel):
    """Question history output payload."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    topic: int = Field(alias="topic_id")
    question: str
    answer: str
    session_id: str
    is_favorited: bool
    feedback_score: int
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        return to_local_iso(value)


class ConversationMessage(BaseModel):
    """Single conversation message for chat UI."""

    role: Literal["user", "assistant"] = Field(
        ..., description="Message role: 'user' or 'assistant'"
    )
    content: str
    timestamp: datetime

    @field_serializer("timestamp")
    def serialize_timestamp(self, value: datetime) -> str:
        return to_local_iso(value)
