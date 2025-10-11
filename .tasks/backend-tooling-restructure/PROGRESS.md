# Backend Tooling Relocation — Progress Log

## 2025-10-11T17:40:32+09:00
- Completed repository-wide audit for `pyproject.toml`, `uv.lock`, `.venv`, `.python-version`, and `uv sync` references:
  - Key consumers: `Dockerfile.backend`, `scripts/docker/dev-entrypoint.sh`, local test scripts (`scripts/test-*.sh`), documentation (`README.md`, `docs/DEPLOYMENT.md`, `backend/README.md`), VSCode settings (`.vscode/settings.json`), pyright configuration (`pyrightconfig.json`), and git hooks.
  - Confirmed absence of GitHub Actions workflows relying on the root manifest (directory empty).
- Decision: retain a minimal root `pyproject.toml` as uv workspace entrypoint listing `backend/` to preserve root-level commands and future multi-service expansion.
- Identified follow-up updates required once manifests relocate:
  - Adjust Dockerfile COPY instructions and `ENV PATH` expectations.
  - Update scripts sourcing `.venv` to either use workspace-aware `uv` commands or backend-local virtualenv path.
  - Revise IDE/tooling configs (`.vscode/settings.json`, `pyrightconfig.json`) to point to backend paths.
  - Refresh docs to instruct running `uv` commands from `backend/` (or clarify workspace usage).
  - Document cleanup guidance for root `.venv`, `.uv_cache`, `.python-version` during migration.

## 2025-10-11T17:55:21+09:00
- Moved backend manifests into service directory (`backend/pyproject.toml`, `backend/uv.lock`, `backend/.python-version`) and converted root `pyproject.toml` into a uv workspace pointing to `backend/`.
- Updated Docker workflow (`Dockerfile.backend`), dev entrypoints, test scripts, VSCode settings, Pyright config, and docs to respect backend-local manifests/virtualenv.
- Adjusted Alembic setup tests to resolve paths relative to repo root and skip backend `.venv`; ensured lint exclusion covers parent `alembic/env.py`.
- Refreshed README/DEPLOYMENT guidance to use subshell `cd backend` patterns; added gitignore entries for backend `.venv`/`.uv_cache`.
- Ran `uv sync --frozen` (backend scope) to bootstrap new environment and `uv run pytest` to confirm green suite (227 passed, 17 skipped, coverage 83.83%).
