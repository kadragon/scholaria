from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from celery.exceptions import Retry


def test_regenerate_embedding_task_success(db_session):
    from backend.tasks.embeddings import regenerate_embedding_task

    context_item_id = 1

    with (
        patch("backend.tasks.embeddings.Session") as mock_session_maker,
        patch(
            "backend.services.ingestion.generate_context_item_embedding"
        ) as mock_generate,
    ):
        mock_db = MagicMock()
        mock_session_maker.return_value.__enter__.return_value = mock_db
        mock_generate.return_value = True

        result = regenerate_embedding_task(context_item_id)

        assert result is True
        mock_generate.assert_called_once_with(mock_db, context_item_id)


def test_regenerate_embedding_task_retry_on_failure(db_session):
    from backend.tasks.embeddings import regenerate_embedding_task

    context_item_id = 1

    with (
        patch("backend.tasks.embeddings.Session") as mock_session_maker,
        patch(
            "backend.services.ingestion.generate_context_item_embedding"
        ) as mock_generate,
        patch("backend.tasks.embeddings.regenerate_embedding_task.retry") as mock_retry,
    ):
        mock_db = MagicMock()
        mock_session_maker.return_value.__enter__.return_value = mock_db
        mock_generate.side_effect = Exception("OpenAI API timeout")
        mock_retry.side_effect = Retry()

        with pytest.raises(Retry):
            regenerate_embedding_task(context_item_id)

        mock_retry.assert_called_once()


def test_regenerate_embedding_task_max_retries_exceeded(db_session):
    from backend.tasks.embeddings import regenerate_embedding_task

    context_item_id = 1

    with (
        patch("backend.tasks.embeddings.Session") as mock_session_maker,
        patch(
            "backend.services.ingestion.generate_context_item_embedding"
        ) as mock_generate,
        patch("backend.tasks.embeddings.regenerate_embedding_task.retry") as mock_retry,
    ):
        mock_db = MagicMock()
        mock_session_maker.return_value.__enter__.return_value = mock_db
        mock_generate.side_effect = Exception("Persistent failure")
        mock_retry.side_effect = Exception("Max retries exceeded")

        with pytest.raises(Exception, match="Max retries exceeded"):
            regenerate_embedding_task(context_item_id)
