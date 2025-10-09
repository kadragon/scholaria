# Research: Backend Coverage Threshold

## Goal
백엔드 테스트 커버리지 측정 및 임계값 설정 (프런트엔드 Phase 4와 대칭)

## Scope
- pytest-cov 설치 및 설정
- 현재 백엔드 커버리지 측정
- 적절한 임계값 설정 (현재 수준 기반)
- pytest.ini 또는 pyproject.toml에 설정 추가

## Related Files & Flows

### 현재 테스트 상태
- **총 테스트**: 134개 백엔드 테스트 통과
- **pytest 설정**: `pytest.ini` (testpaths, markers, filterwarnings)
- **pyproject.toml**: ruff, mypy 설정 존재
- **커버리지 도구**: pytest-cov **미설치**

### 프런트엔드 패턴 참조
- **도구**: vitest + @vitest/coverage-v8
- **임계값**: 25% (lines, functions, branches, statements)
- **설정 위치**: `vitest.config.ts`
- **CI**: coverage 잡 추가

## Hypotheses
1. **pytest-cov** 설치 후 커버리지 측정 가능
2. 현재 커버리지 수준을 기준으로 **현실적 임계값** 설정 (과도한 상향 회피)
3. `pyproject.toml`에 `[tool.pytest.ini_options]` 섹션 추가하여 커버리지 설정 통합 가능
4. CI에 백엔드 커버리지 체크 추가 (GitHub Actions)

## Evidence
- pytest.ini에 커버리지 관련 설정 **없음**
- pyproject.toml에 pytest-cov dependency **없음**
- `uv run pytest --cov` 실행 시 "unrecognized arguments" 에러
- 프런트엔드는 29.63% 커버리지로 25% 임계값 설정

## Assumptions / Open Questions
- **Q1**: 백엔드 현재 커버리지는? → pytest-cov 설치 후 측정 필요
- **Q2**: 임계값은 전체 프로젝트 vs. 테스트된 파일? → 전체 프로젝트 (프런트엔드와 동일)
- **Q3**: CI에서 백엔드 커버리지 잡 추가? → 프런트엔드와 대칭되게 추가
- **Q4**: HTML 리포트 생성? → 로컬 검토용으로 유용, gitignore 필요

## Risks
- 현재 커버리지가 낮을 경우 임계값 설정 시 **즉시 실패** → 점진적 상향 필요
- pytest-cov 추가는 **비파괴적** (기존 테스트 영향 없음)
- CI 잡 추가는 **빌드 시간 증가** (캐시 활용 필요)

## Next
Plan 작성 → pytest-cov 설치 → 커버리지 측정 → 임계값 설정 → CI 추가
