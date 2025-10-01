"""Pydantic schemas for question history endpoints."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from backend.schemas.utils import to_local_iso


class QuestionHistoryOut(BaseModel):
    """Question history output payload."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    topic: int = Field(alias="topic_id")
    question: str
    answer: str
    session_id: str
    is_favorited: bool
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        return to_local_iso(value)
