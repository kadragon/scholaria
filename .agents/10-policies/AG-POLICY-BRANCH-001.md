---
id: AG-POLICY-BRANCH-001
version: 1.0.0
scope: global
status: active
supersedes: []
depends: [AG-POLICY-DEV-GUARDRAILS-001]
last-updated: 2025-10-11
owner: team-admin
---
# Branch Strategy

## Hard Rule
- **Never commit or push directly to `main`.**
- All work happens on feature branches.

## Branch Naming
- `feat/<task-slug>` — new features
- `fix/<issue-slug>` — bug fixes
- `docs/<topic>` — documentation updates
- `refactor/<scope>` — structural improvements
- `chore/<subject>` — maintenance tasks

## Workflow
1. Create branch from latest `main`.
2. Develop with TDD (Red → Green → Refactor).
3. Ensure all quality gates pass (ruff, mypy, pytest).
4. Commit with structured message: `[Structural|Behavioral](<scope>) <summary> [<task-slug>]`.
5. Open PR only after local tests are Green.

## Protection
- CI must pass before merge.
- Squash or rebase to keep history clean.
- Delete branch after merge.
