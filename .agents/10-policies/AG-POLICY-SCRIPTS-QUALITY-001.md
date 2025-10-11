---
id: AG-POLICY-SCRIPTS-QUALITY-001
version: 1.0.0
scope: folder:scripts
status: active
supersedes: []
depends: [AG-FOUND-SCRIPTS-001]
last-updated: 2025-10-11
owner: platform-team
---
# Script Quality Constraints

## Portability
- Preserve POSIX shell compatibility; scripts must run on macOS and Linux without modifications.

## Logging
- Retain established emoji/text prefixes (e.g., `🐳`, `[INFO]`) to keep execution flow readable.

## Dependency Handling
- Abort early when Docker or `uv` is unavailable and print remediation instructions.
- Align health checks with the current service topology (backend, postgres, redis, qdrant, frontend, celery-worker, flower).
