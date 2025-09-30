"""
FastAPI router for Context resource.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.models.base import get_db
from api.models.context import Context
from api.schemas.context import ContextOut

router = APIRouter()


@router.get("/contexts", response_model=list[ContextOut])
def list_contexts(db: Session = Depends(get_db)) -> list[Context]:
    """
    List all contexts.

    Equivalent to Django rag.views.ContextListView.
    """
    contexts = db.query(Context).order_by(Context.name).all()
    return contexts


@router.get("/contexts/{context_id}", response_model=ContextOut)
def get_context(context_id: int, db: Session = Depends(get_db)) -> Context:
    """
    Get a single context by ID.

    Equivalent to Django rag.views.ContextDetailView.
    """
    context = db.query(Context).filter(Context.id == context_id).first()
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")
    return context
