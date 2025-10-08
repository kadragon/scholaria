# Plan: Performance Benchmark

## Objective
RAG 파이프라인의 성능 지표를 정량화하고 목표 달성 여부를 검증하는 테스트 스위트 구현

## Constraints
- TDD 필수: 테스트 먼저 작성 → 구현
- OpenAI API 비용 최소화: Mock 우선, 실제 호출은 필요시만
- 기존 테스트 통과 유지 (134개)
- pytest 마커 활용 (`@pytest.mark.performance`, `@pytest.mark.golden`)

## Target Files & Changes

### New Files
1. **`backend/tests/test_performance_benchmark.py`** - 응답 지연 & 부하 테스트
   - `test_rag_query_response_time_under_3s()` - E2E 지연 측정 (mock)
   - `test_rag_pipeline_step_timings()` - 파이프라인 단계별 측정
   - `test_concurrent_requests_stability()` - 동시 요청 10개 안정성

2. **`backend/tests/fixtures/golden_dataset.json`** - Golden Dataset
   - 20-30개 질문-컨텍스트-기대결과 트리플렛
   - 구조: `[{question, expected_context_ids, topic_id, difficulty}, ...]`

3. **`backend/tests/test_golden_accuracy.py`** - 관련 인용 정확도
   - `test_golden_dataset_citation_accuracy()` - 80% 임계값 검증
   - `test_reranking_improves_relevance()` - 재순위 효과 측정

### Modified Files
4. **`backend/services/rag_service.py`** - 타이밍 메트릭 추가 (선택적)
   - `query()` 메서드에 단계별 타이머 로깅 (DEBUG 레벨)

## Test/Validation Cases

### Performance Tests (@pytest.mark.performance)
1. **Cold start**: 캐시 미스 시나리오, P95 < 5s (완화된 목표)
2. **Warm cache**: 캐시 적중 시나리오, P95 < 1s
3. **Concurrent load**: 10 동시 요청, 모든 요청 성공
4. **Pipeline breakdown**: 각 단계(임베딩/검색/재순위/LLM) 지연 분포

### Golden Dataset Tests (@pytest.mark.golden)
5. **Citation accuracy**: Top-5 재순위 결과에 expected_context_id 포함 비율 ≥ 80%
6. **Reranking gain**: 재순위 전후 정확도 차이 측정

## Steps

### Step 1: Golden Dataset 생성 (Structural)
- [ ] `backend/tests/fixtures/` 디렉터리 생성
- [ ] `golden_dataset.json` 스키마 정의 및 샘플 5개 작성
- [ ] JSON 로딩 헬퍼 함수 작성 (`conftest.py`)

### Step 2: 성능 테스트 - 실패 케이스 (Red)
- [ ] `test_performance_benchmark.py` 작성
  - `test_rag_query_response_time_under_3s` (mock 기반, 타이머 측정)
  - `test_concurrent_requests_stability` (asyncio.gather 사용)
- [ ] 테스트 실행 → **실패 확인** (측정 로직 없음)

### Step 3: 성능 측정 구현 (Green)
- [ ] `AsyncRAGService.query()`에 단계별 타이머 추가 (로깅)
- [ ] 테스트 픽스처에서 mock 타이밍 시뮬레이션
- [ ] 테스트 재실행 → **통과 확인**

### Step 4: Golden Dataset 테스트 - 실패 케이스 (Red)
- [ ] `test_golden_accuracy.py` 작성
  - `test_golden_dataset_citation_accuracy` (실제 Qdrant 호출 필요)
- [ ] Golden Dataset 10개로 확장
- [ ] 테스트 실행 → **실패 가능** (정확도 측정)

### Step 5: 정확도 개선 또는 임계값 조정 (Green)
- [ ] 정확도 < 80% 시: 재순위 파라미터 조정 또는 테스트 데이터 재검토
- [ ] 정확도 ≥ 80% 시: 통과 확인
- [ ] 테스트 재실행 → **통과 확인**

### Step 6: 부하 테스트 확장 (선택적)
- [ ] `test_concurrent_requests_50` 추가 (50 동시 요청)
- [ ] Docker Compose 환경에서 통합 테스트

### Step 7: 문서화 & 커밋
- [ ] PROGRESS.md 작성
- [ ] TASK_SUMMARY.md 생성
- [ ] 브랜치 생성 후 커밋 (feat/performance-benchmark)

## Rollback
- 새 테스트 파일만 추가, 기존 코드 변경 최소 → Git revert로 즉시 롤백 가능
- `rag_service.py` 변경 시 타이머 로직은 DEBUG 레벨이므로 운영 영향 없음

## Review Hotspots
1. **Golden Dataset 품질**: 질문-컨텍스트 매핑 정확성 (수동 검증 필요)
2. **Mock 타이밍 현실성**: 실제 OpenAI/Qdrant 지연과 유사한지 검증
3. **부하 테스트 신뢰성**: asyncio 동시성 vs. 실제 네트워크 부하 차이

## Status
- [ ] Step 1: Golden Dataset 생성
- [ ] Step 2: 성능 테스트 Red
- [ ] Step 3: 성능 측정 Green
- [ ] Step 4: Golden Dataset 테스트 Red
- [ ] Step 5: 정확도 검증 Green
- [ ] Step 6: 부하 테스트 확장
- [ ] Step 7: 문서화 & 커밋
