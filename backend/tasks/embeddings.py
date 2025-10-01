from __future__ import annotations

import logging

from celery import Task

from backend.celery_app import celery_app
from backend.models.base import Session

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)  # type: ignore[misc]
def regenerate_embedding_task(self: Task, context_item_id: int) -> bool:
    with Session() as db:
        try:
            from backend.services.ingestion import generate_context_item_embedding

            result = generate_context_item_embedding(db, context_item_id)
            logger.info(
                f"Successfully regenerated embedding for ContextItem {context_item_id}"
            )
            return result
        except Exception as exc:
            logger.warning(
                f"Failed to regenerate embedding for ContextItem {context_item_id} (attempt {self.request.retries + 1}): {exc}"
            )
            raise self.retry(exc=exc, countdown=60 * (2**self.request.retries)) from exc
