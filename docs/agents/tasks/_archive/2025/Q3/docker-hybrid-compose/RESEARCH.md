# Research: Docker Hybrid Compose

**Goal**
- Enable concurrent Django (port 8000) and FastAPI (port 8001) services via Docker for Phase 1 migration experimentation.

**Scope**
- Development Docker Compose workflows, Dockerfiles, entrypoints, shared dependencies.
- Networking and shared resources (PostgreSQL, Redis, Qdrant).
- Dev workflow documentation alignment (README, API docs).

**Related Files/Flows**
- `docker-compose.dev.yml`, `docker-compose.yml` base services.
- `Dockerfile.dev`, `scripts/docker/dev-entrypoint.sh` (Django).
- FastAPI runtime commands (`api/README.md`, `uvicorn`).
- Potential new entrypoint script(s) for FastAPI container.

**Hypotheses**
- FastAPI service can reuse same Python image with different command & port.
- Shared volume mount of repo is required for hot reload for both services.
- Base `docker-compose.yml` should remain backend services only; dev override will add app containers.

**Evidence**
- `docker-compose.dev.yml` currently defines only `web` (Django) referencing `Dockerfile.dev` and `dev-entrypoint`.
- `api/main.py` includes routers and is ready for ASGI server.
- `api/README.md` documents manual `uvicorn` command (port 8001) — indicates missing Docker support.
- `Dockerfile.dev` installs dev deps; could run uvicorn using same environment.

**Assumptions / Open Questions**
- Will FastAPI container require separate entrypoint script for uvicorn with autoreload? (likely)
- Need for shared environment variables between Django and FastAPI (DB, Redis, etc.).
- Should FastAPI container depend on same services as Django (`postgres`, `redis`, `qdrant`)?
- How to expose FastAPI port configuration (env var?) while keeping defaults.

**Sub-agent Findings**
- N/A

**Risks**
- Port collisions or duplicated migrations if both containers auto-run management commands.
- Environment drift if FastAPI container lacks necessary env vars.
- Hot reload performance if uvicorn reload + volume mount cause conflicts.

**Next**
- Draft implementation plan covering compose updates, entrypoint creation, README instructions, and validation strategy (TDD around Docker?).
