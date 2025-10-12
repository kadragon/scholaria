"""Admin API Pydantic schemas for Refine Admin Panel."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from backend.schemas.utils import to_local_iso


class AdminBaseOut(BaseModel):
    """Base schema for Admin API output with common fields."""

    id: int
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        return to_local_iso(value)

    model_config = ConfigDict(from_attributes=True)


class AdminTopicOut(AdminBaseOut):
    """Topic output schema for Admin API."""

    slug: str
    system_prompt: str
    contexts_count: int = Field(description="Number of associated contexts")
    context_ids: list[int] = Field(
        default_factory=list, description="IDs of associated contexts"
    )


class AdminTopicCreate(BaseModel):
    """Topic create schema for Admin API."""

    name: str = Field(min_length=1, max_length=200)
    slug: str | None = Field(None, min_length=1, max_length=50)
    description: str = Field(default="")
    system_prompt: str = Field(min_length=1)
    context_ids: list[int] = Field(default_factory=list)


class AdminTopicUpdate(BaseModel):
    """Topic update schema for Admin API."""

    name: str | None = Field(None, min_length=1, max_length=200)
    slug: str | None = Field(None, min_length=1, max_length=50)
    description: str | None = None
    system_prompt: str | None = Field(None, min_length=1)
    context_ids: list[int] | None = None


class TopicListResponse(BaseModel):
    """Topic list response for Refine (data + total format)."""

    data: list[AdminTopicOut]
    total: int


class AdminContextOut(AdminBaseOut):
    """Context output schema for Admin API."""

    context_type: str
    chunk_count: int
    processing_status: str
    topics_count: int = Field(default=0, description="Number of associated topics")


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
    topic_ids: list[int] | None = None


class AdminContextItemUpdate(BaseModel):
    """ContextItem update schema for Admin API."""

    content: str | None = Field(None, min_length=1)
    order_index: int | None = Field(None, ge=0)


class AdminFaqQaCreate(BaseModel):
    """FAQ Q&A create schema for Admin API."""

    title: str = Field(min_length=1)
    content: str = Field(min_length=1)


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


class AnalyticsSummaryOut(BaseModel):
    """Analytics summary schema."""

    total_questions: int
    total_feedback: int
    active_sessions: int
    average_feedback_score: float


class TopicStatsOut(BaseModel):
    """Topic statistics schema."""

    topic_id: int
    topic_name: str
    question_count: int
    average_feedback_score: float


class QuestionTrendOut(BaseModel):
    """Question trend schema (time series)."""

    date: str
    question_count: int


class FeedbackDistributionOut(BaseModel):
    """Feedback score distribution schema."""

    positive: int
    neutral: int
    negative: int


class FeedbackCommentOut(BaseModel):
    """Individual feedback comment entry for analytics."""

    history_id: int
    topic_id: int
    topic_name: str
    feedback_score: int
    feedback_comment: str
    created_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return to_local_iso(value)


class ProcessingStatusResponse(BaseModel):
    """Response schema for context processing status."""

    status: str = Field(
        description="Processing status: PENDING, PROCESSING, COMPLETED, FAILED"
    )
    progress: int = Field(ge=0, le=100, description="Progress percentage (0-100)")
