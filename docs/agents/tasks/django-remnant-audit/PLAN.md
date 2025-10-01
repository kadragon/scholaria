# Plan: Django Remnant Audit

## Objective
FastAPI 전용 프로젝트에서 Django 관련 잔재물을 제거하고, asgiref 의존성을 FastAPI native async 패턴으로 전환하여 코드베이스를 정리한다.

## Constraints
- 기존 테스트가 통과해야 함 (특히 RAG 엔드포인트 테스트)
- 성능 저하가 없어야 함 (async 전환 시)
- 외부 API 변경 없음 (내부 구현만 변경)

## Target Files & Changes

### 1. Remove asgiref dependency usage
**File**: `backend/services/rag_service.py`
- **Change**: `sync_to_async` 4개 호출을 FastAPI native async 패턴으로 전환
  - L116: `generate_embedding` → async 메서드로 직접 호출 또는 thread pool 사용
  - L121: `search_similar` → async 메서드로 직접 호출
  - L137: `rerank_results` → async 메서드로 직접 호출
- **Strategy**:
  - Option A: 해당 서비스들을 async 메서드로 리팩터링 (권장)
  - Option B: `asyncio.to_thread()` 사용 (Python 3.9+, sync 코드 유지하면서 async 호환)
  - 선택: **Option B** (더 안전하고 기존 동기 코드 재사용)

### 2. Documentation review (optional)
**Files**: `README.md`, `docs/DEPLOYMENT.md`, `docs/ARCHITECTURE_DECISIONS.md`
- **Change**: Django 언급 제거 또는 "과거 Django 기반" 컨텍스트로 업데이트
- **Priority**: Low (코드 변경이 우선)

## Test/Validation Cases
1. RAG 엔드포인트 테스트 (`backend/tests/test_rag_endpoint.py`) 통과 확인
2. 관련 서비스 단위 테스트 통과 확인
3. `uv run ruff check .` 통과
4. `uv run mypy .` 통과
5. 전체 테스트 스위트 실행: `uv run pytest`

## Steps
1. [ ] `backend/services/rag_service.py` 리팩터링
   - [ ] `sync_to_async` import 제거
   - [ ] 4개 호출을 `asyncio.to_thread()` 로 전환
   - [ ] TDD: 기존 테스트 통과 확인
2. [ ] 타입 체크 및 린트 검증
3. [ ] 전체 테스트 스위트 실행
4. [ ] (선택) 문서 업데이트
5. [ ] AGENTS.md 업데이트 (결정 기록)

## Rollback
- Git stash 또는 commit 전 상태로 복원
- asgiref 패턴은 동작하는 것으로 검증되었으므로 안전 복구 가능

## Review Hotspots
- `rag_service.py:114-150`: async 전환 로직의 정확성
- 임베딩/검색/리랭킹 서비스의 동기성 가정이 여전히 유효한지 확인

## Status
- [ ] Step 1: rag_service.py 리팩터링
- [ ] Step 2: 타입 체크 및 린트
- [ ] Step 3: 전체 테스트
- [ ] Step 4: 문서 업데이트 (선택)
- [ ] Step 5: AGENTS.md 업데이트
