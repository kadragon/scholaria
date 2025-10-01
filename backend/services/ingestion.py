from __future__ import annotations

import logging
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.context import Context, ContextItem

logger = logging.getLogger(__name__)


def ingest_document(
    db: Session,
    context_id: int,
    file_path: str,
    title: str,
    context_type: str,
) -> int:
    """
    Ingest a document into the system (PDF/Markdown/FAQ).

    Args:
        db: SQLAlchemy session
        context_id: ID of the Context to associate with
        file_path: Path to the file
        title: Title for the document
        context_type: Type of context (PDF, MARKDOWN, FAQ)

    Returns:
        Number of chunks created

    Raises:
        ValueError: If context not found or parsing fails
        FileNotFoundError: If file doesn't exist
    """
    logger.info(f"Starting {context_type} ingestion: {title} (context_id={context_id})")

    context = db.scalar(select(Context).where(Context.id == context_id))
    if not context:
        error_msg = f"Context not found: {context_id}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    from backend.ingestion.strategies import get_ingestion_strategy

    try:
        strategy = get_ingestion_strategy(context_type)
    except ValueError as e:
        logger.error(str(e))
        raise

    try:
        content = strategy.parse(file_path)
        logger.info(
            f"{context_type} parsed successfully: {len(content) if content else 0} characters"
        )
    except FileNotFoundError:
        logger.error(f"{context_type} file not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"{context_type} parsing failed for {file_path}: {e}")
        raise ValueError(f"{context_type} parsing failed: {e}") from e

    if not content:
        logger.warning(f"Empty content from {context_type}: {file_path}")
        return 0

    try:
        chunks = strategy.chunk(content)
        logger.info(f"{context_type} content chunked into {len(chunks)} pieces")
    except Exception as e:
        logger.error(f"Chunking failed for {file_path}: {e}")
        raise ValueError(f"Text chunking failed: {e}") from e

    if not chunks:
        logger.warning(f"No chunks created from {context_type}: {file_path}")
        return 0

    ingestion_timestamp = datetime.now(UTC).isoformat()

    import json

    items_to_create = [
        ContextItem(
            title=f"{title} - Chunk {i}",
            content=chunk,
            context_id=context_id,
            file_path=file_path,
            item_metadata=json.dumps(
                {
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "chunk_size": len(chunk),
                    "content_type": context_type.lower(),
                    "ingestion_timestamp": ingestion_timestamp,
                }
            ),
        )
        for i, chunk in enumerate(chunks, 1)
    ]

    db.add_all(items_to_create)
    db.flush()

    logger.info(f"Created {len(chunks)} ContextItems for {context_type}: {title}")

    return len(chunks)


def save_uploaded_file(file_content: bytes, suffix: str = ".tmp") -> Path:
    """
    Save uploaded file content to a temporary file.

    Args:
        file_content: Raw file bytes
        suffix: File suffix (e.g., '.pdf')

    Returns:
        Path to the temporary file

    Raises:
        IOError: If file write fails
    """
    try:
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp_file.write(file_content)
        tmp_file.flush()
        tmp_file.close()
        return Path(tmp_file.name)
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise OSError(f"Failed to save uploaded file: {e}") from e


def delete_temp_file(file_path: Path) -> None:
    """
    Delete a temporary file safely.

    Args:
        file_path: Path to the file to delete
    """
    try:
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted temporary file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to delete temporary file {file_path}: {e}")


def generate_context_item_embedding(db: Session, context_item_id: int) -> bool:
    """
    Generate and store embedding for a ContextItem.

    Args:
        db: SQLAlchemy session
        context_item_id: ID of the ContextItem to generate embedding for

    Returns:
        True if embedding was generated successfully, False otherwise

    Raises:
        ValueError: If ContextItem doesn't exist or has no content
    """
    logger.info(f"Generating embedding for ContextItem {context_item_id}")

    context_item = db.scalar(
        select(ContextItem).where(ContextItem.id == context_item_id)
    )
    if not context_item:
        error_msg = f"ContextItem not found: {context_item_id}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if not context_item.content:
        logger.warning(f"No content found for ContextItem {context_item_id}")
        return False

    try:
        from backend.retrieval.embeddings import EmbeddingService
        from backend.retrieval.qdrant import QdrantService

        embedding_service = EmbeddingService()
        qdrant_service = QdrantService()

        qdrant_service.create_collection()

        embedding = embedding_service.generate_embedding(context_item.content)

        import json

        item_metadata_str = (
            context_item.item_metadata
            if hasattr(context_item, "item_metadata")
            else None
        )
        item_metadata: dict[str, object] = (
            json.loads(item_metadata_str)
            if item_metadata_str and isinstance(item_metadata_str, str)
            else {}
        )

        qdrant_service.store_embedding(
            context_item_id=context_item.id,
            embedding=embedding,
            metadata={
                "chunk_index": item_metadata.get("chunk_index", 0),
                "source_file": item_metadata.get("source_file", ""),
            },
        )

        logger.info(
            f"Successfully generated embedding for ContextItem {context_item_id}"
        )
        return True

    except Exception as e:
        logger.error(
            f"Failed to generate embedding for ContextItem {context_item_id}: {e}"
        )
        raise
