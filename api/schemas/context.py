"""
Pydantic schemas for Context and ContextItem resources.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


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


class ContextWithItemsOut(ContextOut):
    """Context output schema with items included."""

    items: list[ContextItemOut] = []
