# Backend Tooling Relocation — Plan

## Objectives
- Move uv-managed manifests into `backend/` while preserving developer and CI workflows.
- Introduce (or confirm) root-level uv workspace configuration for future multi-service alignment.

## Strategy
1. **Audit & Prep**
   - Enumerate references to `pyproject.toml`, `uv.lock`, `.venv`, `.python-version`, and `uv sync` across repo (scripts, Docker, CI, docs, IDE config).
   - Decide workspace posture: keep a minimalist root `pyproject.toml` declaring a uv workspace with `backend/` member.
2. **Relocate Manifests**
   - Copy `pyproject.toml` and `uv.lock` into `backend/`; adjust paths inside if necessary (e.g., `[tool.hatch.build.targets.wheel]` packages path).
   - Replace root `pyproject.toml` with workspace-only manifest referencing `backend/pyproject.toml` (or remove if redundant per uv semantics) and ensure `.gitignore` rules cover relocated artifacts.
   - Handle `.python-version`, `.venv`, `.uv_cache`: decide to relocate, regenerate, or document cleanup.
3. **Update Tooling**
   - Update `Dockerfile.backend`, compose entrypoints, scripts, and documentation to target `backend/pyproject.toml` and `backend/uv.lock`.
   - Adjust VSCode settings, pyright config, and any CI workflows under `.github/workflows/` that rely on the root manifest.
   - Ensure Alembic/Docker paths remain accurate after move.
4. **TDD Cycle & Verification**
   - Run `uv run ruff check .`, `uv run mypy .`, and `uv run pytest` from `backend/` (workspace aware) ensuring green.
   - From repo root, execute equivalent checks via workspace to confirm parity.
   - Perform `docker build -f Dockerfile.backend .` dry-run (build to cache) or `docker compose build backend` to validate container paths.
5. **Documentation & Cleanup**
   - Update contributor docs (`README.md`, `docs/DEPLOYMENT.md`, `backend/README.md`) with new instructions.
   - Record decisions and status in `PROGRESS.md`; prepare summary for archiving when done.

## Testing & Validation
- Unit & lint commands executed from `backend/` and repo root.
- Docker image build to ensure manifest copy paths resolve.
- Optional: `scripts/docker/dev-entrypoint.sh` smoke-run to verify `uv sync` still succeeds (may require container execution).

## Rollback Plan
- Retain copies of original root manifests for quick restoration.
- Revert Dockerfile and scripts to prior commit if container build fails.
- Reset workspace manifest to original state if uv commands stop working from root.
