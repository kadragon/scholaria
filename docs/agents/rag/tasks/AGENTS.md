# RAG Tasks - Agent Knowledge Base

## Intent

- Celery task definitions for document ingestion, embedding generation, and monitoring.

## Constraints

- Preserve Celery `bind=True` semantics; direct calls must keep monitoring-friendly return values.
- Instantiate chunkers via `rag.ingestion.chunkers` module attributes so tests can patch dependencies.
- Use `uv run pytest` for fast feedback on task behaviors and monitoring tests.
- Guard `self.request` access—`id`, `called_directly`, and `eta` may be missing when tasks run synchronously in tests.

## Context

- `rag/tasks.py` delegates ingestion per context type and shares logging patterns across PDF/FAQ/Markdown paths.
- Markdown, FAQ, and PDF ingestion use shared chunker configuration; mocking relies on module-level lookups (`chunkers_module.*`).

## Changelog

- Updated ingestion tasks to resolve monitoring test by looking up chunkers via module attribute, keeping mocks effective while preserving production behavior.
- Added `_extract_task_request_metadata` helper so PDF/FAQ/Markdown ingestion safely persist chunk metadata even when Celery request fields are absent.
