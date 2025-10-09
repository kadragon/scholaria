# Plan: Golden Dataset Integration Testing

## Objective
Golden Dataset을 활용해 **실제 Qdrant 벡터 검색** 통합 테스트를 구현하고, 리랭킹 후 Top-5 결과의 **관련 인용 정확도 80% 이상** 검증

## Constraints
- TDD 필수 (Red → Green → Refactor)
- Redis + Qdrant 서비스 필요 (Docker Compose 기반)
- OpenAI API 호출 최소화 (임베딩 캐시 활용 또는 fixture 사전 생성)
- 기존 mock 기반 테스트는 유지 (성능 벤치마크는 별도 유지)
- 통합 테스트는 `@pytest.mark.integration` 마커로 격리

## Target Files & Changes

### 신규 파일
1. **`backend/tests/test_golden_integration.py`** (신규)
   - `@pytest.mark.integration` 마커 적용
   - Fixture: `integration_db_with_golden_data` — Topic/Context/ContextItem + Qdrant 시딩
   - 테스트 1: `test_rag_pipeline_with_real_qdrant` — 5개 질문 실행 → 정확도 검증
   - 테스트 2: `test_reranking_improves_accuracy_integration` — 리랭킹 전후 비교

### 수정 파일
2. **`backend/tests/conftest.py`**
   - Fixture 추가: `integration_db_with_golden_data(db_session, golden_dataset)`
   - Qdrant 컬렉션 초기화 + 임베딩 삽입 (fixture 또는 사전 생성된 임베딩 사용)
   - AsyncRAGService 인스턴스 생성 (Redis + Qdrant 실제 연결)

3. **`pytest.ini`**
   - 마커 정의 추가: `integration: Integration tests requiring external services`
   - 기존 `golden`, `performance` 마커는 유지

### 데이터 준비 (선택적)
4. **`backend/tests/fixtures/golden_embeddings.json`** (옵션)
   - 5개 질문 + 관련 문서 임베딩 사전 생성 (OpenAI API 호출 1회만)
   - 테스트 속도 향상 + 비용 절감

## Test & Validation Cases

### Test 1: `test_rag_pipeline_with_real_qdrant`
**Red (실패 조건)**
- 통합 DB에 샘플 Topic/Context/ContextItem 존재
- Qdrant에 임베딩 삽입 완료
- Golden dataset 5개 질문 실행 → 각 질문마다 `AsyncRAGService.query()` 호출
- **Expected**: Top-5 reranked 결과에 `expected_context_ids` 포함 비율 ≥ 80%
- **Actual (초기)**: Qdrant 미연결 또는 데이터 없음 → 정확도 0%

**Green (통과 조건)**
- Fixture에서 실제 문서 삽입 + 임베딩 생성 (또는 사전 생성된 임베딩 로드)
- `AsyncRAGService.query()` 실행 → Qdrant 검색 → BGE 리랭킹
- 정확도 계산: `total_hits / total_expected >= 0.8`

**Validation**
- 각 질문마다 `reranked_results`에 최소 1개 expected_context_id 포함
- 5개 질문 전체 정확도 80% 이상

---

### Test 2: `test_reranking_improves_accuracy_integration`
**Red (실패 조건)**
- 리랭킹 전 Qdrant raw search 결과(Top-5) 정확도 계산
- 리랭킹 후 BGE reranker 결과(Top-5) 정확도 계산
- **Expected**: 리랭킹 후 정확도 - 리랭킹 전 정확도 ≥ 0.10 (10% 개선)
- **Actual (초기)**: BGE reranker mock → 실제 개선 없음

**Green (통과 조건)**
- `RerankingService.rerank_results()` 실제 호출
- Baseline(Qdrant 벡터 검색) vs. Reranked(BGE) 정확도 비교
- 개선폭 ≥ 0.10 확인

**Validation**
- `reranked_accuracy >= baseline_accuracy`
- `reranked_accuracy - baseline_accuracy >= 0.1`

## Steps (TDD)

### Step 1: 통합 테스트 인프라 구축
1. **pytest.ini 마커 추가** — `integration` 마커 정의
2. **conftest.py fixture 작성** — `integration_db_with_golden_data`
   - Topic 3개 생성 (id: 1, 2, 3)
   - Context 18개 생성 (test_golden_accuracy.py의 FAKE_CONTEXTS 기반)
   - ContextItem 생성 + 임베딩 (OpenAI API 또는 fixture 로드)
   - Qdrant 컬렉션 리셋 + 임베딩 upsert
3. **Docker Compose 확인** — `docker-compose.dev.yml`에 Qdrant/Redis 서비스 존재 확인

**Commit**: `[Structural] (tests) Add integration test infrastructure [golden-dataset-benchmark]`

---

### Step 2: 실패하는 통합 테스트 작성 (Red)
4. **`test_golden_integration.py` 생성**
   - `test_rag_pipeline_with_real_qdrant` 작성
   - `test_reranking_improves_accuracy_integration` 작성
5. **테스트 실행** — `uv run pytest -m integration -v`
   - **예상 결과**: `FAILED` (Qdrant 데이터 없음 또는 임베딩 미생성)

**Commit**: `[Behavioral] (tests) Add failing integration tests for golden dataset [golden-dataset-benchmark]`

---

### Step 3: Fixture 구현 (Green)
6. **conftest.py에 샘플 데이터 생성 로직 추가**
   - `FAKE_CONTEXTS` 기반으로 Context/ContextItem 생성
   - 임베딩 생성 (Option A: OpenAI API 실시간 호출 + Redis 캐시, Option B: 사전 생성 fixture)
   - Qdrant 삽입 (`qdrant_service.store_embedding`)
7. **테스트 재실행** — `uv run pytest -m integration -v`
   - **예상 결과**: `PASSED` (정확도 80% 달성 여부는 샘플 데이터 품질에 따라 조정)

**Commit**: `[Behavioral] (tests) Implement integration fixture with Qdrant seeding [golden-dataset-benchmark]`

---

### Step 4: 정확도 검증 로직 강화 (Refactor)
8. **정확도 계산 함수 분리** — `_calculate_accuracy(results, expected_ids)` 헬퍼 함수
9. **리랭킹 개선폭 검증** — `test_reranking_improves_accuracy_integration` 통과 확인
10. **테스트 커버리지 확인** — `uv run pytest --cov=backend.services.rag_service -m integration`

**Commit**: `[Structural] (tests) Refactor accuracy calculation helpers [golden-dataset-benchmark]`

---

### Step 5: CI 통합 준비 (Optional)
11. **GitHub Actions 워크플로 수정** — `.github/workflows/test.yml`
    - Redis/Qdrant 서비스 컨테이너 추가 또는 `--skip-integration` 옵션
12. **README 업데이트** — 통합 테스트 실행 방법 문서화

**Commit**: `[Structural] (docs) Document integration test setup [golden-dataset-benchmark]`

---

### Step 6: 최종 검증
13. **전체 테스트 실행** — `uv run pytest`
    - 기존 테스트 (134개) + 통합 테스트 (2개) 모두 통과 확인
14. **Lint/Type check** — `uv run ruff check . && uv run mypy .`

**Commit**: `[Behavioral] (tests) Complete golden dataset integration tests [golden-dataset-benchmark]`

## Rollback Strategy

1. **Fixture 실패 시** — `integration_db_with_golden_data` fixture 제거 → 통합 테스트 skip
2. **Qdrant 연결 실패 시** — `pytest.skip("Qdrant service not available")`로 graceful skip
3. **OpenAI API 실패 시** — 사전 생성된 임베딩 fixture 사용 (golden_embeddings.json)
4. **전체 롤백** — 브랜치 삭제 후 main 복귀 (`git branch -D feat/golden-dataset-benchmark`)

## Review Hotspots

1. **conftest.py Fixture** — Qdrant 임베딩 삽입 로직 (병렬 실행 안전성)
2. **OpenAI API 호출** — 비용/레이트 제한 고려 (캐시 또는 fixture 우선)
3. **정확도 기준점** — 80% 달성 불가능 시 기준 하향 조정 (예: 60% 초기 목표)
4. **CI 통합** — Docker 서비스 의존성 (로컬 개발 환경 필요)

## Status
- [ ] Step 1: 통합 테스트 인프라 구축 (pytest.ini + conftest fixture)
- [ ] Step 2: 실패하는 통합 테스트 작성 (Red)
- [ ] Step 3: Fixture 구현 (Green)
- [ ] Step 4: 정확도 검증 로직 강화 (Refactor)
- [ ] Step 5: CI 통합 준비 (Optional)
- [ ] Step 6: 최종 검증 (전체 테스트 + lint)
