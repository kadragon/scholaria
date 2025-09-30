"""
Pydantic schemas for Topic resource.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


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
