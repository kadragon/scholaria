"""
Pydantic schemas for Context and ContextItem resources.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer

from backend.schemas.utils import to_local_iso


class ContextItemOut(BaseModel):
    """ContextItem output schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    context_id: int
    file_path: str | None = None
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        return to_local_iso(value)


class ContextBase(BaseModel):
    """Base Context schema with common fields."""

    name: str
    description: str
    context_type: str
    original_content: str | None = None
    chunk_count: int = 0
    processing_status: str = "PENDING"


class ContextOut(ContextBase):
    """Context output schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        return to_local_iso(value)


class ContextWithItemsOut(ContextOut):
    """Context output schema with items included."""

    items: list[ContextItemOut] = []


class ContextCreate(BaseModel):
    """Schema for creating a new Context."""

    name: str
    description: str
    context_type: str
    original_content: str | None = None


class ContextUpdate(BaseModel):
    """Schema for updating an existing Context (partial updates)."""

    name: str | None = None
    description: str | None = None
    original_content: str | None = None


class FAQQACreate(BaseModel):
    """Schema for adding a Q&A pair to FAQ context."""

    title: str
    content: str
