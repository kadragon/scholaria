# Backend Tooling Relocation — Spec Delta

## Acceptance Criteria
1. Root `pyproject.toml` either becomes a uv workspace manifest pointing to `backend/` **or** is removed entirely if redundant; resulting layout must satisfy "Target End State" from 2025-10-11 restructure spec.
2. `backend/pyproject.toml` and `backend/uv.lock` exist with identical dependency metadata to current root manifest prior to the move.
3. All automation artifacts (Dockerfiles, scripts, CI workflows, docs) successfully reference the new backend-relative manifest paths without manual intervention.
4. Local developer workflows (`uv sync`, linting, mypy, pytest) run successfully when invoked from both repository root (using workspace) and `backend/` directory.
5. Containerized workflows (`docker compose`, `Dockerfile.backend`) build without modifications beyond updated paths.

## Contract Updates
- uv workspace root (if kept) MUST list `backend` package path and refrain from redefining dependency metadata.
- Backend manifest MUST continue exporting `backend` as the primary package for hatch builds.
- Virtual environment directories MUST be ignored via `.gitignore` regardless of location; no stray root-level uv artifacts remain post-move.

## Examples & Scenarios
- Running `uv sync` within `backend/` installs dependencies identical to pre-move environment.
- Running `uv run ruff check backend` from repo root resolves backend dependencies through workspace.
- `docker build -f Dockerfile.backend .` succeeds, copying manifests from `backend/` instead of root.

## Migration Notes
- Remove or relocate existing `.venv`, `.uv_cache`, `.python-version` at root if necessary; document manual cleanup steps where automatic relocation is not feasible.
- Update docs to instruct contributors to run `uv` commands from `backend/` (or root with workspace) post-move.
