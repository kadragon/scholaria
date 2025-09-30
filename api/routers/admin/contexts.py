"""Contexts Admin API for Refine Admin Panel."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencies.auth import require_admin
from api.models.base import get_db
from api.models.user import User

router = APIRouter(prefix="/contexts", tags=["Admin - Contexts"])


@router.get("/")
async def list_contexts(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    """List all contexts with pagination (Refine format)."""
    # TODO: Implement list logic
    return {"data": [], "total": 0}
