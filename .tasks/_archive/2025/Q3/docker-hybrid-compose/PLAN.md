# Plan: Docker Hybrid Compose

**Objective**
- Provide Docker-based hybrid runtime where Django (`web`) and FastAPI (`fastapi`) services run concurrently for Phase 1 migration testing.

**Constraints**
- Strict TDD: add failing test before compose updates.
- Keep Docker base services untouched unless necessary.
- Maintain hot-reload developer experience.
- Avoid impacting existing Django workflows.

**Target Files & Changes**
- `rag/tests/` (new test verifying compose setup).
- `docker-compose.dev.yml` (add `fastapi` service configuration).
- `scripts/docker/` (add FastAPI dev entrypoint).
- `Dockerfile.dev` (ensure compatibility if adjustments needed).
- `README.md` and `api/README.md` (document new workflow).
- `docs/agents/TASKS.md` (mark Phase 1 subtask once complete).

**Test / Validation Cases**
- Pytest: new test ensuring FastAPI service definition (port, command, dependencies) exists in `docker-compose.dev.yml`.
- Optional manual validation: `docker compose -f docker-compose.yml -f docker-compose.dev.yml up fastapi` (document as next step; not run in automation).

**Steps**
1. Add failing pytest covering FastAPI service expectations in dev compose.
2. Implement FastAPI Docker service: entrypoint script, compose updates, env vars, volumes.
3. Update documentation for dual-server usage; adjust Dockerfile if needed.
4. Run targeted tests (new test, fastapi tests) to confirm green; document residual manual validation follow-up.

**Rollback**
- Revert `docker-compose.dev.yml`, new script, and documentation changes; remove added tests.

**Review Hotspots**
- Ensure no duplicate container naming collisions.
- Confirm env var parity with Django to prevent DB access issues.
- Validate port mappings and reload commands to avoid watch conflicts.

**Status**
- [x] Step 1: Test added (fails as expected)
- [x] Step 2: FastAPI service implemented
- [x] Step 3: Documentation updated
- [x] Step 4: Tests executed
