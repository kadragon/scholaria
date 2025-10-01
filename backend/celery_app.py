from __future__ import annotations

from celery import Celery

from backend.config import settings

celery_app = Celery(
    "scholaria",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["backend.tasks.embeddings"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
)
