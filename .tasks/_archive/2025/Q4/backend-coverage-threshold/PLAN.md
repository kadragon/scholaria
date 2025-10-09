# Plan: Backend Coverage Threshold

## Objective
백엔드 테스트 커버리지 임계값 설정 및 CI 통합 (프런트엔드 Phase 4와 대칭)

## Constraints
- 현재 커버리지 85% 유지
- 기존 195개 테스트 통과 유지
- 임계값은 **현실적 수준** (현재 85%에서 **80%** 설정으로 회귀 방지)

## Target Files & Changes

### 1. `pyproject.toml`
- `[tool.pytest.ini_options]` 섹션에 커버리지 설정 추가
- `--cov=backend`, `--cov-report=term-missing`, `--cov-report=html`
- `--cov-fail-under=80` (임계값 80%)

### 2. `.gitignore`
- `htmlcov/` 추가 (커버리지 HTML 리포트 제외)
- `.coverage` 추가 (커버리지 데이터 파일 제외)

### 3. `.github/workflows/` (신규 또는 기존 확장)
- 백엔드 CI 워크플로 존재 여부 확인
- coverage 잡 추가 또는 기존 test 잡에 커버리지 옵션 추가

### 4. `README.md` (선택)
- 백엔드 테스트 섹션에 커버리지 정보 추가

## Test/Validation Cases

### 커버리지 임계값
- **T1**: `uv run pytest` 실행 시 80% 미달이면 실패
- **T2**: 현재 85% 커버리지로 임계값 통과
- **T3**: HTML 리포트 생성 확인 (`htmlcov/index.html`)

### CI 워크플로
- **T4**: PR 생성 시 백엔드 coverage 체크 실행
- **T5**: 잡 실패 시 PR 블로킹

## Steps

### Step 1: pyproject.toml 커버리지 설정 (TDD)
- [ ] Red: pytest.ini_options에 `--cov-fail-under=80` 추가
- [ ] Green: `uv run pytest` 실행 → 85% 통과 확인
- [ ] Refactor: 커버리지 리포트 옵션 정리

### Step 2: .gitignore 업데이트 (Structural)
- [ ] `htmlcov/`, `.coverage` 추가

### Step 3: CI 워크플로 확인 및 추가 (Structural)
- [ ] `.github/workflows/` 디렉토리 검토
- [ ] 백엔드 CI 워크플로 존재 시 커버리지 옵션 추가
- [ ] 미존재 시 신규 `backend-ci.yml` 생성

### Step 4: 문서화 및 검증
- [ ] README 업데이트 (커버리지 정보)
- [ ] 로컬 테스트 실행 + CI 트리거 확인

## Rollback
- Step 1: pyproject.toml에서 커버리지 설정 제거
- Step 2: .gitignore에서 htmlcov/, .coverage 제거
- Step 3: CI 워크플로 변경 revert

## Review Hotspots
- 현재 85% 커버리지에서 80% 임계값 설정 → **여유 5%**로 안정적
- pytest-cov 의존성 추가는 **비파괴적**
- CI 잡 추가 시 **빌드 시간** 고려 (현재 16초로 빠름)

## Status
- [ ] Step 1: pyproject.toml 커버리지 설정
- [ ] Step 2: .gitignore 업데이트
- [ ] Step 3: CI 워크플로 추가
- [ ] Step 4: 문서화 및 검증
