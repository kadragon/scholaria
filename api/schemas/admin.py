"""Admin API Pydantic schemas for Refine Admin Panel."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AdminTopicOut(BaseModel):
    """Topic output schema for Admin API."""

    id: int
    name: str
    description: str
    system_prompt: str
    contexts_count: int = Field(description="Number of associated contexts")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminTopicCreate(BaseModel):
    """Topic create schema for Admin API."""

    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="")
    system_prompt: str = Field(min_length=1)
    context_ids: list[int] = Field(default_factory=list)


class AdminTopicUpdate(BaseModel):
    """Topic update schema for Admin API."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    system_prompt: str | None = Field(None, min_length=1)
    context_ids: list[int] | None = None


class TopicListResponse(BaseModel):
    """Topic list response for Refine (data + total format)."""

    data: list[AdminTopicOut]
    total: int
