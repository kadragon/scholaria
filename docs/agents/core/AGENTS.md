# Core Django App - Agent Knowledge Base

## Intent

Global Django configuration, settings, and project-wide utilities for Scholaria.

## Constraints

- Keep settings deterministic across environments; default to secure, production-friendly values.
- Avoid dangling configuration variables for removed services; prune env vars in tandem with dependency changes.
- Ensure new settings carry sensible defaults and are documented in `docs/`.

## Context

- `core/settings.py` defines service connectivity (PostgreSQL, Redis, Qdrant, MinIO) and OpenAI configuration.
- PDF parsing now uses Docling in-process—no `UNSTRUCTURED_API_URL`; remove orphaned env vars when migrating integrations.
- Quality gates (ruff, mypy, pytest) rely on settings defaults aligning with `core.test_settings`.

## Changelog

- 2025-09-21: Implemented Context Management System Enhancement - removed MinIO dependency for PDF storage, added upload → parse → chunk → discard file workflow, updated admin interface for PDF-specific workflow
- 2025-09-20: Removed Unstructured API URL setting after migrating PDF parser to Docling.
