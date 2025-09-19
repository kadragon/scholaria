from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from celery import shared_task
from django.db import transaction

from .ingestion.chunkers import TextChunker
from .ingestion.parsers import FAQParser, MarkdownParser, PDFParser
from .models import Context, ContextItem

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(ConnectionError,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)  # type: ignore[misc]
def process_document(self: Any, context_id: int, file_path: str, title: str) -> str:
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
    try:
        logger.info(f"Processing document: {title} (context_id={context_id})")

        # Validate inputs
        if not isinstance(context_id, int) or context_id <= 0:
            raise ValueError(f"Invalid context_id: {context_id}")

        if not file_path or not isinstance(file_path, str):
            raise ValueError(f"Invalid file_path: {file_path}")

        if not title or not isinstance(title, str):
            raise ValueError(f"Invalid title: {title}")

        # Get context with error handling
        try:
            context = Context.objects.get(id=context_id)
        except Context.DoesNotExist:
            logger.error(f"Context not found: {context_id}")
            raise

        TASK_MAP = {
            "PDF": ingest_pdf_document,
            "MARKDOWN": ingest_markdown_document,
            "FAQ": ingest_faq_document,
        }
        task_to_run = TASK_MAP.get(context.context_type)

        if task_to_run:
            try:
                task = task_to_run.delay(context_id, file_path, title)
                logger.info(
                    f"Delegated to {task_to_run.__name__} with task_id: {task.id}"
                )
                return task.id
            except Exception as e:
                logger.error(f"Failed to delegate task: {e}")
                raise
        else:
            error_msg = f"Unsupported context type: {context.context_type}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    except Exception as e:
        logger.error(f"Error in process_document: {e}", exc_info=True)
        raise


@shared_task(
    bind=True,
    autoretry_for=(ConnectionError, IOError),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)  # type: ignore[misc]
def ingest_pdf_document(self: Any, context_id: int, file_path: str, title: str) -> int:
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
        FileNotFoundError: If PDF file doesn't exist
        ValueError: If parsing fails
    """
    try:
        logger.info(f"Starting PDF ingestion: {title} (context_id={context_id})")

        # Get context with error handling
        try:
            context = Context.objects.get(id=context_id)
        except Context.DoesNotExist:
            logger.error(f"Context not found for PDF ingestion: {context_id}")
            raise

        # Parse the PDF with error handling
        try:
            parser = PDFParser()
            content = parser.parse_file(file_path)
            logger.info(
                f"PDF parsed successfully: {len(content) if content else 0} characters"
            )
        except FileNotFoundError:
            logger.error(f"PDF file not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"PDF parsing failed for {file_path}: {e}")
            # Retry for transient errors, fail for permanent errors
            if "network" in str(e).lower() or "timeout" in str(e).lower():
                raise self.retry(countdown=60, max_retries=3) from e
            raise ValueError(f"PDF parsing failed: {e}") from e

        if not content:
            logger.warning(f"Empty content from PDF: {file_path}")
            return 0

        # Chunk the content with error handling
        try:
            chunker = TextChunker(chunk_size=1000, overlap=200)
            chunks = chunker.chunk_text(content)
            logger.info(f"Content chunked into {len(chunks)} pieces")
        except Exception as e:
            logger.error(f"Chunking failed for {file_path}: {e}")
            raise ValueError(f"Text chunking failed: {e}") from e

        if not chunks:
            logger.warning(f"No chunks created from PDF: {file_path}")
            return 0

        # Create ContextItem for each chunk with database transaction
        try:
            with transaction.atomic():
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
                            "task_id": self.request.id,
                            "ingestion_timestamp": self.request.called_directly
                            or self.request.eta,
                        },
                    )
                    for i, chunk in enumerate(chunks, 1)
                ]
                ContextItem.objects.bulk_create(items_to_create)
                logger.info(f"Created {len(chunks)} ContextItems for PDF: {title}")

        except Exception as e:
            logger.error(f"Database write failed for PDF {file_path}: {e}")
            raise

        return len(chunks)

    except Exception as e:
        logger.error(f"PDF ingestion failed for {title}: {e}", exc_info=True)
        raise


@shared_task(
    bind=True,
    autoretry_for=(ConnectionError, IOError),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)  # type: ignore[misc]
def ingest_faq_document(self: Any, context_id: int, file_path: str, title: str) -> int:
    """
    Ingest an FAQ document into the system.

    Args:
        context_id: ID of the Context to associate with
        file_path: Path to the FAQ file
        title: Title for the document

    Returns:
        Number of chunks created

    Raises:
        Context.DoesNotExist: If context doesn't exist
        FileNotFoundError: If FAQ file doesn't exist
        ValueError: If parsing fails
    """
    try:
        logger.info(f"Starting FAQ ingestion: {title} (context_id={context_id})")

        # Get context with error handling
        try:
            context = Context.objects.get(id=context_id)
        except Context.DoesNotExist:
            logger.error(f"Context not found for FAQ ingestion: {context_id}")
            raise

        # Parse the FAQ with error handling
        try:
            parser = FAQParser()
            content = parser.parse_file(file_path)
            logger.info(
                f"FAQ parsed successfully: {len(content) if content else 0} characters"
            )
        except FileNotFoundError:
            logger.error(f"FAQ file not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"FAQ parsing failed for {file_path}: {e}")
            raise ValueError(f"FAQ parsing failed: {e}") from e

        if not content:
            logger.warning(f"Empty content from FAQ: {file_path}")
            return 0

        # Chunk the content with error handling
        try:
            chunker = TextChunker(chunk_size=1000, overlap=200)
            chunks = chunker.chunk_text(content)
            logger.info(f"FAQ content chunked into {len(chunks)} pieces")
        except Exception as e:
            logger.error(f"FAQ chunking failed for {file_path}: {e}")
            raise ValueError(f"FAQ text chunking failed: {e}") from e

        if not chunks:
            logger.warning(f"No chunks created from FAQ: {file_path}")
            return 0

        # Create ContextItem for each chunk with database transaction
        try:
            with transaction.atomic():
                items_to_create = [
                    ContextItem(
                        title=f"{title} - FAQ Chunk {i}",
                        content=chunk,
                        context=context,
                        file_path=file_path,
                        metadata={
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "chunk_size": len(chunk),
                            "content_type": "faq",
                            "task_id": self.request.id,
                            "ingestion_timestamp": self.request.called_directly
                            or self.request.eta,
                        },
                    )
                    for i, chunk in enumerate(chunks, 1)
                ]
                ContextItem.objects.bulk_create(items_to_create)
                logger.info(f"Created {len(chunks)} FAQ ContextItems for: {title}")

        except Exception as e:
            logger.error(f"Database write failed for FAQ {file_path}: {e}")
            raise

        return len(chunks)

    except Exception as e:
        logger.error(f"FAQ ingestion failed for {title}: {e}", exc_info=True)
        raise


@shared_task(
    bind=True,
    autoretry_for=(ConnectionError, IOError),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)  # type: ignore[misc]
def ingest_markdown_document(
    self: Any, context_id: int, file_path: str, title: str
) -> int:
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
        FileNotFoundError: If Markdown file doesn't exist
        ValueError: If parsing fails
    """
    try:
        logger.info(f"Starting Markdown ingestion: {title} (context_id={context_id})")

        # Get context with error handling
        try:
            context = Context.objects.get(id=context_id)
        except Context.DoesNotExist:
            logger.error(f"Context not found for Markdown ingestion: {context_id}")
            raise

        # Parse the Markdown with error handling
        try:
            parser = MarkdownParser()
            content = parser.parse_file(file_path)
            logger.info(
                f"Markdown parsed successfully: {len(content) if content else 0} characters"
            )
        except FileNotFoundError:
            logger.error(f"Markdown file not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Markdown parsing failed for {file_path}: {e}")
            raise ValueError(f"Markdown parsing failed: {e}") from e

        if not content:
            logger.warning(f"Empty content from Markdown: {file_path}")
            return 0

        # Chunk the content with error handling
        try:
            chunker = TextChunker(chunk_size=1000, overlap=200)
            chunks = chunker.chunk_text(content)
            logger.info(f"Markdown content chunked into {len(chunks)} pieces")
        except Exception as e:
            logger.error(f"Markdown chunking failed for {file_path}: {e}")
            raise ValueError(f"Markdown text chunking failed: {e}") from e

        if not chunks:
            logger.warning(f"No chunks created from Markdown: {file_path}")
            return 0

        # Create ContextItem for each chunk with database transaction
        try:
            with transaction.atomic():
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
                            "content_type": "markdown",
                            "task_id": self.request.id,
                            "ingestion_timestamp": self.request.called_directly
                            or self.request.eta,
                        },
                    )
                    for i, chunk in enumerate(chunks, 1)
                ]
                ContextItem.objects.bulk_create(items_to_create)
                logger.info(f"Created {len(chunks)} Markdown ContextItems for: {title}")

        except Exception as e:
            logger.error(f"Database write failed for Markdown {file_path}: {e}")
            raise

        return len(chunks)

    except Exception as e:
        logger.error(f"Markdown ingestion failed for {title}: {e}", exc_info=True)
        raise
