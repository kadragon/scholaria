# Contributing to Scholaria

Scholaria 프로젝트 기여 가이드 - TDD 워크플로우 & 품질 유지 원칙

> 📚 **관련 문서**:
> - [README.md](../README.md) - 개발 환경 설정 & 빠른 시작
> - [TESTING_STRATEGY.md](TESTING_STRATEGY.md) - TDD 원칙 & 테스트 실행
> - [ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md) - 기술 결정 배경
> - [DEPLOYMENT.md](DEPLOYMENT.md) - 프로덕션 배포

## Project Philosophy

Scholaria is built around disciplined engineering:

- Embrace **tdd** to evolve the system safely.
- Always honor the **red → green → refactor** cycle.
- Apply **tidy first** before introducing behavioral changes.
- Keep deployments production-ready at all times.

## Before You Start

1. **작업 목록 확인**: `docs/agents/TASKS.md`에서 현재 우선순위 파악
2. **폴더별 컨텍스트**: 관련 `docs/agents/<folder>/AGENTS.md` 읽기
3. **개발 환경 준비**: [README.md](../README.md) 참조
   - Python 3.13+, Docker, uv 설치 필요
4. **테스트 전략 숙지**: [TESTING_STRATEGY.md](TESTING_STRATEGY.md) 읽기

## Workflow Overview

1. Pick the next actionable item from `docs/tasks.md`.
2. Capture folder rules from `docs/agents/.../AGENTS.md` before touching files.
3. Write the smallest failing test that describes the change.
4. Implement just enough code or docs to make the test pass.
5. Run the full quality suite.
6. Refactor when green, keeping structural and behavioral changes separate.
7. Open a pull request with context linked to the task tracker.

## Branching Strategy

- Create feature branches from `main` using the format `feature/<slug>` or `fix/<slug>`.
- Keep branches short-lived; merge once tests and reviews pass.
- Rebase frequently to avoid diverging from `main`.

## Coding Standards

- Follow the monorepo structure (`backend/` FastAPI services, `frontend/` Refine admin) and reuse existing modules before adding new ones.
- Prefer explicit imports and type annotations everywhere.
- Document complex logic inline only when intent is not obvious.
- Use existing utilities from `backend/` services and shared helpers before adding new abstractions.
- Respect formatting enforced by Ruff; avoid hand-formatting that fights tooling.

## Testing Requirements

Run the full suite locally before pushing:

```bash
uv run ruff check .
uv run mypy .
uv run pytest
docker-compose up -d --build
```

- Keep tests parallel-safe (pytest runs with xdist in CI).
- Add regression tests for every bug fix.
- Skip brittle time-based or network-dependent assertions.

## Commit Guidelines

- Use the format `[Structural]` or `[Behavioral]` at the start of commit messages.
- Keep commits focused on a single logical change.
- Write descriptive subjects (≤ 72 characters) and, when needed, include detailed bodies.
- Confirm lint, type, and test checks are green before committing.

## Pull Request Checklist

Before requesting review:

- [ ] Confirm the branch rebases cleanly onto `main`.
- [ ] Ensure all checks pass locally (`uv run ruff check .`, `uv run mypy .`, `uv run pytest`).
- [ ] Provide screenshots or logs for UI or operational changes.
- [ ] Link to the relevant entry in `docs/tasks.md` and any related issues.
- [ ] Verify new docs or code reference the correct `AGENTS.md` learnings.

## Communication

- Use Slack for quick questions and async updates; escalate blockers early.
- File feature requests and bugs using the GitHub issue template to maintain a searchable history.
- Document new folder-specific insights in the mirrored `docs/agents/` path when a task closes.
- Summaries of completed work should be added to `docs/tasks.md` before closing tickets.

## Support

- Consult existing issue template examples for formatting guidance.
- Reach out via Slack `#scholaria-dev` for pairing or review requests.
- Update the relevant `AGENTS.md` file whenever you discover a repeatable rule or pitfall.
- If unsure about architecture decisions, schedule a quick design huddle with the platform team.
