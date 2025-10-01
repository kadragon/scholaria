# Plan: Django Remnant Audit

## Objective
- Confirm the repository no longer depends on Django and remove or flag residual artifacts.

## Constraints
- Follow TDD where code changes are required.
- Avoid disruptive deletions without evidence; prefer minimal adjustments.

## Target Files & Changes
- Configuration and env files (`.env*`, docs, docker compose).
- Backend dependencies (`pyproject.toml`, requirements, scripts).
- CI scripts and documentation referencing Django.

## Test / Validation Cases
- Static search for `django` references yields only historical docs.
- All automated tests (if run) pass without Django context.

## Steps
1. Map current Django references via ripgrep and document findings.
2. Classify references (code, config, docs, deps) and decide actions.
3. Write failing test or check if removal requires safety net.
4. Remove/adjust residuals with minimal changes.
5. Update docs/AGENTS as needed.
6. Run relevant tests/linters if modifications performed.

## Rollback
- Revert modified files to previous state via git if changes introduce regressions.

## Review Hotspots
- `backend/`, `scripts/`, `docs/`, Docker configs, env files.

- [x] Step 1: inventory references (ripgrep sweep completed)
- [x] Step 2: classify and decide actions (grouped into runtime code, tooling/env, documentation)
- [x] Step 3: add guard tests if needed (pytest import guard written)
- [x] Step 4: apply fixes (removed `django` imports, updated tooling & env)
- [x] Step 5: documentation update (core docs/agents refreshed for FastAPI stack)
- [ ] Step 6: validation
