# Backend Tooling Relocation — Research

## Context & Scope
- Align the repository with the "Monorepo Restructure Spec — Backend Tooling" dated 2025-10-11.
- Scope limited to moving uv-managed artifacts (`pyproject.toml`, `uv.lock`, virtualenv metadata) beneath `backend/` and adapting tooling that currently assumes root-level placement.
- Out of scope: frontend assets, runtime code changes unrelated to path updates, dependency upgrades.

## Current Layout Observations
- Root hosts `pyproject.toml`, `uv.lock`, `.venv`, `.python-version`, and uv cache directories.
- Backend sources live in `backend/` while CI/CD scripts, Dockerfiles, and documentation target the root manifest.
- `Dockerfile.backend` copies `pyproject.toml` and `uv.lock` from root into every build stage (builder, development, production).
- `scripts/docker/dev-entrypoint.sh` invokes `uv sync --dev` from `/app`, expecting manifest presence at the working directory.
- Documentation (`README.md`, `docs/DEPLOYMENT.md`, `backend/README.md`) instructs contributors to run `uv sync` from repository root.
- VSCode settings (`.vscode/settings.json`) configure Ruff using `./pyproject.toml` relative to repo root.

## Tooling & Config Dependencies
- GitHub Actions workflows (to be confirmed) likely reference root manifest; need audit.
- `pyrightconfig.json` and `pytest.ini` reside at root and implicitly rely on `backend/` module packaging via `[tool.hatch.build.targets.wheel]` pointing to `backend`.
- Docker Compose backend service mounts project root, so entrypoints rely on virtualenv stored under `/app/.venv` or pipx-managed environment after `uv sync`.
- `.gitignore` currently excludes `.venv`, `uv.lock`, etc. Must ensure patterns remain valid once files move under `backend/`.

## Hypotheses & Risks
- Moving manifests without updating Dockerfiles and scripts will break container builds and local dev workflows (`uv sync` failure due to missing `pyproject.toml`).
- Introducing a uv workspace at root allows future multi-service Python packages; decision impacts how developers invoke `uv` commands from root.
- IDE tooling (VSCode, Pyright) may require explicit workspace path adjustments to maintain lint/type-check coverage.
- Cached virtualenv directories (`.venv`, `.uv_cache`) may need relocation or regeneration; ensure cleanup instructions cover them.

## Evidence References
- `Dockerfile.backend:17-55` — copies and relies on root-level `pyproject.toml`/`uv.lock`.
- `scripts/docker/dev-entrypoint.sh:7` — executes `uv sync --dev` assuming cwd contains pyproject.
- `README.md:16` & `docs/DEPLOYMENT.md:33` — root `uv sync` instructions.
- `.vscode/settings.json` — uses `./pyproject.toml` for Ruff configuration.
- Root `.python-version` present; uv may regenerate inside backend once manifests move.

## Open Questions for Spec Alignment
- Should root retain a minimalist `pyproject.toml` declaring a uv workspace pointing to `backend/`? Needed if root-level commands (`uv sync`) must remain valid.
- How to treat existing root `.venv` and `.uv_cache` directories: relocate under `backend/` or regenerate on demand?
- Do GitHub Actions cache keys rely on root-relative manifest path?

## Next Research Actions
- Enumerate every repo reference to `pyproject.toml`, `uv.lock`, `.venv`, and `uv sync` to scope rename updates.
- Confirm CI workflow assumptions inside `.github/workflows/` for uv commands and path references.
- Decide workspace strategy (root workspace vs backend-only manifest) before implementation plan is finalized.
