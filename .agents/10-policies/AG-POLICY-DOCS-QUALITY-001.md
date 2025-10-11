---
id: AG-POLICY-DOCS-QUALITY-001
version: 1.0.0
scope: folder:docs
status: active
supersedes: []
depends: [AG-FOUND-DOCS-001]
last-updated: 2025-10-11
owner: docs-team
---
# Documentation Quality Rules

## Synchronization
- Keep documentation synchronized with tests; update any test constants derived from headings whenever names change.
- Reflect Docling as the in-process parsing dependency; avoid references to deprecated Unstructured APIs.

## Authoring Style
- Lead every file with a purpose-aligned H1 heading.
- Prioritize actionable scenarios and runnable commands over descriptive prose.
- Use Markdown exclusively; cross-link specs when doc changes have acceptance criteria impact.
