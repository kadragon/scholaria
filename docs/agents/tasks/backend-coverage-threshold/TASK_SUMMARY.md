# Task Summary: Backend Coverage Threshold

## Goal
백엔드 테스트 커버리지 임계값 설정 및 CI 통합 (프런트엔드 Phase 4와 대칭)

## Core Changes
1. **`pyproject.toml`**: pytest-cov dependency 추가, `[tool.pytest.ini_options]` 섹션에 80% 임계값 설정
2. **`.gitignore`**: htmlcov/ 추가
3. **`.github/workflows/backend-ci.yml`**: 3개 잡 (test+coverage, lint, typecheck) 신규 생성
4. **`README.md`**: 테스트 섹션 업데이트 (85% coverage, 80% threshold)

## Tests
- 195 passed, 2 skipped
- 커버리지 85.01% (80% 임계값 통과)
- ruff, mypy 클린

## Commits
- `[Structural] feat(backend): Add coverage threshold and CI workflow [backend-coverage-threshold]`
