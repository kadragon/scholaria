"""
FastAPI router for Context resource.
"""

import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.dependencies.auth import require_admin
from backend.models.base import get_db
from backend.models.context import Context, ContextItem
from backend.schemas.admin import AdminContextItemUpdate
from backend.schemas.context import (
    ContextItemOut,
    ContextOut,
    ContextUpdate,
    FAQQACreate,
)

logger = logging.getLogger(__name__)

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
    url: str | None = Form(None),
    db: Session = Depends(get_db),
) -> Context:
    """
    Create a new context.

    For PDF contexts, file upload is required.
    For Markdown/FAQ contexts, file is optional.
    For WEBSCRAPER contexts, URL is required.
    """
    if context_type not in ["PDF", "MARKDOWN", "FAQ", "WEBSCRAPER"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid context_type. Must be PDF, MARKDOWN, FAQ, or WEBSCRAPER.",
        )

    if context_type == "PDF" and not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File upload is required for PDF contexts.",
        )

    if context_type == "WEBSCRAPER" and not url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL is required for WEBSCRAPER contexts.",
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

    if context_type == "PDF" and file:
        _process_pdf_upload(context, file, db)
    elif context_type == "WEBSCRAPER" and url:
        _process_webscraper_upload(context, url, db)

    return context


def _process_pdf_upload(context: Context, file: UploadFile, db: Session) -> None:
    """Process PDF file upload: parse → chunk → save."""
    from backend.services.ingestion import (
        delete_temp_file,
        ingest_document,
        save_uploaded_file,
    )

    file_content = file.file.read()
    temp_path = save_uploaded_file(file_content, suffix=".pdf")

    try:
        num_chunks, text_content = ingest_document(
            db=db,
            context_id=context.id,
            file_path=str(temp_path),
            title=context.name,
            context_type="PDF",
        )

        context.original_content = text_content
        context.processing_status = "COMPLETED" if num_chunks > 0 else "FAILED"
        db.commit()

    except Exception as e:
        logger.error(f"PDF processing failed for context {context.id}: {e}")
        context.processing_status = "FAILED"
        db.commit()
        raise

    finally:
        delete_temp_file(temp_path)


def _process_webscraper_upload(context: Context, url: str, db: Session) -> None:
    """Process web scraper URL: scrape → chunk → save."""
    from backend.services.ingestion import ingest_document

    try:
        num_chunks, text_content = ingest_document(
            db=db,
            context_id=context.id,
            title=context.name,
            context_type="WEBSCRAPER",
            url=url,
        )

        context.original_content = text_content
        context.processing_status = "COMPLETED" if num_chunks > 0 else "FAILED"
        db.commit()

    except Exception as e:
        logger.error(f"Web scraping failed for context {context.id}: {e}")
        context.processing_status = "FAILED"
        db.commit()
        raise


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


@router.get("/contexts/{context_id}/items", response_model=list[ContextItemOut])
def get_context_items(
    context_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[ContextItem]:
    """
    Get all items for a specific context with pagination.
    """
    context = db.query(Context).filter(Context.id == context_id).first()
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")

    items = (
        db.query(ContextItem)
        .filter(ContextItem.context_id == context_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return items


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


@router.patch(
    "/contexts/{context_id}/items/{item_id}",
    response_model=ContextItemOut,
    dependencies=[Depends(require_admin)],
)
def update_context_item(
    context_id: int,
    item_id: int,
    data: AdminContextItemUpdate,
    db: Session = Depends(get_db),
) -> ContextItem:
    """
    Update a context item (content only for now).
    """
    context = db.query(Context).filter(Context.id == context_id).first()
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")

    item = (
        db.query(ContextItem)
        .filter(ContextItem.id == item_id, ContextItem.context_id == context_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Context item not found")

    if data.content is not None:
        item.content = data.content

    db.commit()
    db.refresh(item)

    if data.content is not None:
        from backend.tasks.embeddings import regenerate_embedding_task

        regenerate_embedding_task.delay(item.id)

    return item
