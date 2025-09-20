# Docs Folder - Agent Knowledge Base

## Intent

Centralized product documentation (guides, playbooks, contributor docs) for Scholaria.

## Constraints

- Mirror engineering practices documented in tests; every major guide should have matching regression tests under `rag/tests/`.
- Keep headings stable—tests assert exact section titles for critical guides.
- Reference `docs/tasks.md` and folder-specific `AGENTS.md` workflows whenever describing process.

## Context

- `CONTRIBUTING.md` defines contributor workflow emphasizing TDD, "red → green → refactor", and "Tidy First"; update tests alongside structural changes.
- Existing guides (`ADMIN_GUIDE`, `USER_GUIDE`, `DEPLOYMENT`) follow instructional tone with actionable checklists and command snippets.
- Deployment guide now documents Docling as an in-process dependency (no external Unstructured API env vars).
- Add new documentation in Markdown with top-level heading matching file purpose and actionable subsections.
