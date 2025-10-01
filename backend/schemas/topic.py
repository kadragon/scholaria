"""
Pydantic schemas for Topic resource.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from backend.schemas.context import ContextOut
from backend.schemas.utils import to_local_iso


class TopicBase(BaseModel):
    """Base Topic schema with common fields."""

    name: str
    description: str
    system_prompt: str | None = None


class TopicOut(TopicBase):
    """Topic output schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    contexts: list[ContextOut] = Field(default_factory=list)

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        return to_local_iso(value)
