from __future__ import annotations

from typing import TYPE_CHECKING

from celery import shared_task

from .ingestion.chunkers import TextChunker
from .ingestion.parsers import MarkdownParser, PDFParser
from .models import Context, ContextItem

if TYPE_CHECKING:
    pass


@shared_task  # type: ignore[misc]
def process_document(context_id: int, file_path: str, title: str) -> str:
    """
    Process a document based on its context type.

    Args:
        context_id: ID of the Context to associate with
        file_path: Path to the document file
        title: Title for the document

    Returns:
        Task ID of the delegated ingestion task

    Raises:
        ValueError: If context type is not supported
        Context.DoesNotExist: If context doesn't exist
    """
    context = Context.objects.get(id=context_id)

    TASK_MAP = {
        "PDF": ingest_pdf_document,
        "MARKDOWN": ingest_markdown_document,
    }
    task_to_run = TASK_MAP.get(context.context_type)

    if task_to_run:
        task = task_to_run.delay(context_id, file_path, title)
        return task.id
    else:
        raise ValueError(f"Unsupported context type: {context.context_type}")


@shared_task  # type: ignore[misc]
def ingest_pdf_document(context_id: int, file_path: str, title: str) -> int:
    """
    Ingest a PDF document into the system.

    Args:
        context_id: ID of the Context to associate with
        file_path: Path to the PDF file
        title: Title for the document

    Returns:
        Number of chunks created

    Raises:
        Context.DoesNotExist: If context doesn't exist
    """
    context = Context.objects.get(id=context_id)

    # Parse the PDF
    parser = PDFParser()
    content = parser.parse_file(file_path)

    if not content:
        return 0

    # Chunk the content
    chunker = TextChunker(chunk_size=1000, overlap=200)
    chunks = chunker.chunk_text(content)

    # Create ContextItem for each chunk
    items_to_create = [
        ContextItem(
            title=f"{title} - Chunk {i}",
            content=chunk,
            context=context,
            file_path=file_path,
            metadata={
                "chunk_index": i,
                "total_chunks": len(chunks),
                "chunk_size": len(chunk),
            },
        )
        for i, chunk in enumerate(chunks, 1)
    ]
    ContextItem.objects.bulk_create(items_to_create)

    return len(chunks)


@shared_task  # type: ignore[misc]
def ingest_markdown_document(context_id: int, file_path: str, title: str) -> int:
    """
    Ingest a Markdown document into the system.

    Args:
        context_id: ID of the Context to associate with
        file_path: Path to the Markdown file
        title: Title for the document

    Returns:
        Number of chunks created

    Raises:
        Context.DoesNotExist: If context doesn't exist
    """
    context = Context.objects.get(id=context_id)

    # Parse the Markdown
    parser = MarkdownParser()
    content = parser.parse_file(file_path)

    if not content:
        return 0

    # Chunk the content
    chunker = TextChunker(chunk_size=1000, overlap=200)
    chunks = chunker.chunk_text(content)

    # Create ContextItem for each chunk
    items_to_create = [
        ContextItem(
            title=f"{title} - Chunk {i}",
            content=chunk,
            context=context,
            file_path=file_path,
            metadata={
                "chunk_index": i,
                "total_chunks": len(chunks),
                "chunk_size": len(chunk),
            },
        )
        for i, chunk in enumerate(chunks, 1)
    ]
    ContextItem.objects.bulk_create(items_to_create)

    return len(chunks)
