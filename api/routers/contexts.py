"""
FastAPI router for Context resource.
"""

import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from api.dependencies.auth import require_admin
from api.models.base import get_db
from api.models.context import Context, ContextItem
from api.schemas.context import (
    ContextItemOut,
    ContextOut,
    ContextUpdate,
    FAQQACreate,
)

router = APIRouter()

MAX_UPLOAD_SIZE = 100 * 1024 * 1024


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


@router.post(
    "/contexts",
    response_model=ContextOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_context(
    name: str = Form(...),
    description: str = Form(...),
    context_type: str = Form(...),
    original_content: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
) -> Context:
    """
    Create a new context.

    For PDF contexts, file upload is required.
    For Markdown/FAQ contexts, file is optional.
    """
    if context_type not in ["PDF", "MARKDOWN", "FAQ"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid context_type. Must be PDF, MARKDOWN, or FAQ.",
        )

    if context_type == "PDF" and not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File upload is required for PDF contexts.",
        )

    if file:
        if file.size and file.size > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum limit ({MAX_UPLOAD_SIZE} bytes).",
            )

        if context_type == "PDF" and file.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported for PDF context type.",
            )

    context = Context(
        name=name,
        description=description,
        context_type=context_type,
        original_content=original_content,
        processing_status="PENDING",
    )
    db.add(context)
    db.commit()
    db.refresh(context)

    if file and context_type == "PDF":
        _process_pdf_upload(context, file, db)

    return context


def _process_pdf_upload(context: Context, file: UploadFile, db: Session) -> None:
    """Process PDF file upload: parse → chunk → save."""
    from rag.ingestion.chunkers import TextChunker
    from rag.ingestion.parsers import PDFParser

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file.file.read())
        temp_path = tmp_file.name

    try:
        parser = PDFParser()
        text = parser.parse_file(temp_path)

        chunker = TextChunker()
        chunks = chunker.chunk_text(text)

        for idx, chunk_text in enumerate(chunks):
            chunk = ContextItem(
                title=f"{context.name} - Chunk {idx + 1}",
                content=chunk_text,
                context_id=context.id,
            )
            db.add(chunk)

        context.original_content = text
        context.processing_status = "PROCESSING"
        db.commit()

    finally:
        Path(temp_path).unlink(missing_ok=True)


@router.put(
    "/contexts/{context_id}",
    response_model=ContextOut,
    dependencies=[Depends(require_admin)],
)
def update_context_full(
    context_id: int,
    data: ContextUpdate,
    db: Session = Depends(get_db),
) -> Context:
    """
    Update a context (full update).
    """
    context = db.query(Context).filter(Context.id == context_id).first()
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")

    if data.name is not None:
        context.name = data.name
    if data.description is not None:
        context.description = data.description
    if data.original_content is not None:
        context.original_content = data.original_content

    db.commit()
    db.refresh(context)
    return context


@router.patch(
    "/contexts/{context_id}",
    response_model=ContextOut,
    dependencies=[Depends(require_admin)],
)
def update_context_partial(
    context_id: int,
    data: ContextUpdate,
    db: Session = Depends(get_db),
) -> Context:
    """
    Update a context (partial update).
    """
    context = db.query(Context).filter(Context.id == context_id).first()
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")

    if data.name is not None:
        context.name = data.name
    if data.description is not None:
        context.description = data.description
    if data.original_content is not None:
        context.original_content = data.original_content

    db.commit()
    db.refresh(context)
    return context


@router.delete(
    "/contexts/{context_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_context(
    context_id: int,
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a context and all its items (CASCADE).
    """
    context = db.query(Context).filter(Context.id == context_id).first()
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")

    db.delete(context)
    db.commit()


@router.post(
    "/contexts/{context_id}/qa",
    response_model=ContextItemOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def add_faq_qa(
    context_id: int,
    data: FAQQACreate,
    db: Session = Depends(get_db),
) -> ContextItem:
    """
    Add a Q&A pair to a FAQ context.
    """
    context = db.query(Context).filter(Context.id == context_id).first()
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")

    if context.context_type != "FAQ":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only add Q&A pairs to FAQ contexts.",
        )

    qa_item = ContextItem(
        title=data.title,
        content=data.content,
        context_id=context.id,
    )
    db.add(qa_item)
    db.commit()
    db.refresh(qa_item)

    return qa_item
