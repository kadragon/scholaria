"""Admin API Pydantic schemas for Refine Admin Panel."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AdminTopicOut(BaseModel):
    """Topic output schema for Admin API."""

    id: int
    name: str
    description: str
    system_prompt: str
    contexts_count: int = Field(description="Number of associated contexts")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


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


class AdminContextOut(BaseModel):
    """Context output schema for Admin API."""

    id: int
    name: str
    description: str
    context_type: str
    chunk_count: int
    processing_status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminContextCreate(BaseModel):
    """Context create schema for Admin API."""

    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="")
    context_type: str = Field(description="PDF, MARKDOWN, or FAQ")
    original_content: str | None = None


class AdminContextUpdate(BaseModel):
    """Context update schema for Admin API."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    original_content: str | None = None


class AdminContextItemUpdate(BaseModel):
    """ContextItem update schema for Admin API."""

    content: str | None = Field(None, min_length=1)


class ContextListResponse(BaseModel):
    """Context list response for Refine (data + total format)."""

    data: list[AdminContextOut]
    total: int


class BulkAssignContextRequest(BaseModel):
    """Request schema for bulk assigning contexts to a topic."""

    context_ids: list[int] = Field(
        min_length=1, description="List of context IDs to assign"
    )
    topic_id: int = Field(description="Target topic ID")


class BulkAssignContextResponse(BaseModel):
    """Response schema for bulk assign operation."""

    assigned_count: int
    topic_id: int


class BulkRegenerateEmbeddingsRequest(BaseModel):
    """Request schema for bulk regenerating embeddings."""

    context_ids: list[int] = Field(
        min_length=1, description="List of context IDs to regenerate"
    )


class BulkRegenerateEmbeddingsResponse(BaseModel):
    """Response schema for bulk regenerate embeddings operation."""

    queued_count: int
    task_ids: list[str]


class BulkUpdateSystemPromptRequest(BaseModel):
    """Request schema for bulk updating topic system prompts."""

    topic_ids: list[int] = Field(
        min_length=1, description="List of topic IDs to update"
    )
    system_prompt: str = Field(min_length=1, description="New system prompt")


class BulkUpdateSystemPromptResponse(BaseModel):
    """Response schema for bulk update system prompt operation."""

    updated_count: int
