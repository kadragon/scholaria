"""
Pydantic schemas for RAG endpoints.
"""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Citation schema for RAG responses."""

    title: str
    content: str
    score: float
    context_type: str
    context_item_id: int


class QuestionRequest(BaseModel):
    """Request schema for asking a question."""

    topic_id: int = Field(..., gt=0, description="Topic ID must be positive")
    question: str = Field(..., min_length=1, description="Question cannot be empty")


class AnswerResponse(BaseModel):
    """Response schema for RAG answers."""

    answer: str
    citations: list[Citation]
    topic_id: int
