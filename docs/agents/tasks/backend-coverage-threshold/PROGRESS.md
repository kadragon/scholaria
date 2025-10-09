# Progress: Backend Coverage Threshold

## Summary
백엔드 테스트 커버리지 임계값 설정 및 CI 통합 완료

## Goal & Approach
- **Goal**: 백엔드 85% 커버리지 유지, 80% 임계값 설정 → CI 통합
- **Approach**: pytest-cov 설치 → pyproject.toml 설정 → CI 추가 → 문서화

## Completed Steps
- ✅ pytest-cov 설치 (uv add pytest-cov --dev)
- ✅ 초기 커버리지 측정 (85.01%, 4224 lines, 633 missed)
- ✅ pyproject.toml에 80% 임계값 설정 (`--cov-fail-under=80`)
- ✅ .gitignore에 htmlcov/ 추가
- ✅ .github/workflows/backend-ci.yml 생성 (test+coverage, lint, typecheck 3개 잡)
- ✅ README.md 업데이트 (테스트 섹션 확장)

## Current Failures
없음 (195 passed, 2 skipped, 85% coverage)

## Decision Log
- **커버리지 기준**: 현재 85%에서 **80% 임계값** 설정 (5% 여유)
- **CI 구조**: 3개 잡 병렬 (test+coverage, lint, typecheck) → uv cache 활용
- **설정 위치**: pyproject.toml `[tool.pytest.ini_options]` (pytest.ini와 병행)
- **HTML 리포트**: htmlcov/ 생성, .gitignore 추가

## Next Step
커밋 및 아티팩트 정리
