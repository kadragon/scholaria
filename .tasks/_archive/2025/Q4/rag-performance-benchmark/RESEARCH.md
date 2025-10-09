# Research: RAG 성능 벤치마크

## Goal
실제 환경에서 RAG 시스템 성능 검증 (80% recall, <3s latency, 동시 사용자 부하)

## Scope
- 응답 품질 (관련 인용 반환율)
- 응답 속도 (평균, p95, p99)
- 동시 부하 처리 능력
- 메모리 사용량

## Related Files/Flows

### 기존 성능 테스트 인프라
- **`rag/tests/golden_dataset.py` (395 lines)**:
  - 24개 golden test cases (ML 주제)
  - 난이도별 (easy/medium/hard)
  - 카테고리별 (fundamentals/architectures/training/applications)
  - expected_keywords, expected_topics 포함

- **`rag/tests/performance_benchmarks.py` (442 lines)**:
  - `PerformanceBenchmark` 클래스
  - `measure_response_time()`: 단일 쿼리 응답 시간
  - `run_concurrent_benchmark()`: 동시 쿼리 (10 workers)
  - `run_load_test()`: 부하 테스트 (100 requests)
  - `measure_memory_usage()`: 메모리 사용량
  - `generate_performance_report()`: 종합 리포트

- **`rag/tests/test_golden_dataset.py`**:
  - golden dataset 검증 테스트
  - keyword matching, relevance scoring
  - 80% pass 기준

- **`rag/tests/test_performance_benchmarks.py`**:
  - 단위 테스트 (mocked RAGService)
  - concurrent/load test 시나리오

## Hypotheses

### H1: 기존 벤치마크 코드 재사용 가능
- **근거**: 이미 구현된 `PerformanceBenchmark` 클래스
- **검증**: 실제 RAG 서비스에 적용 테스트

### H2: 현재 성능이 요구사항 충족
- **요구사항**:
  - 80% 이상 쿼리에서 관련 인용 반환
  - 평균 응답 시간 < 3초
  - 동시 사용자 10명 처리 가능
- **검증**: 벤치마크 실행 후 확인

### H3: 병목은 임베딩/검색 단계
- **근거**: Qdrant 벡터 검색, OpenAI API 호출
- **검증**: 단계별 프로파일링

## Evidence

### 기존 테스트 커버리지
```python
# golden_dataset.py에서 발견된 테스트 케이스 구조
{
    "question": "What are neural networks?",
    "expected_keywords": ["neural networks", "nodes", "layers", ...],
    "expected_topics": ["neural networks", "machine learning"],
    "difficulty": "easy",
    "category": "fundamentals",
    "description": "Basic definition"
}
```

### PerformanceBenchmark 기능
```python
class PerformanceBenchmark:
    def measure_response_time(rag_service, query, topic_ids) -> float
    def run_concurrent_benchmark(rag_service, queries, topic_ids, workers=10) -> list[ConcurrentQueryResult]
    def run_load_test(rag_service, query, topic_ids, num_requests=100) -> LoadTestResult
    def measure_memory_usage(rag_service, query, topic_ids) -> MemoryUsageResult
    def generate_performance_report(...) -> PerformanceReport
```

### 성능 임계값
- `three_second_threshold = 3.0` (하드코딩)
- p95, p99 percentile 계산 지원
- 메모리 delta 측정 (baseline vs peak)

## Assumptions/Open Qs

### 가정
1. **테스트 데이터 존재**: golden dataset의 질문에 답변할 수 있는 Context가 DB에 있음
2. **Qdrant 실행 중**: 벡터 검색 서비스 가동 필요
3. **OpenAI API 키**: 답변 생성을 위한 API 접근 가능

### 열린 질문
1. **Q: 현재 DB에 ML 관련 Context가 있는가?**
   - A: 확인 필요 → 없으면 샘플 데이터 생성
2. **Q: 실제 프로덕션 환경 vs 개발 환경 차이?**
   - A: 벤치마크는 개발 환경에서 실행, 프로덕션 추정
3. **Q: 동시 사용자 목표는?**
   - A: TASKS.md에서 명시 안됨 → 10명으로 가정

## Sub-agent Findings
없음 (단일 에이전트)

## Risks

### High
- **테스트 데이터 부족**: golden dataset 질문에 답변할 Context 없음
  - **완화**: 샘플 PDF/Markdown 업로드 (ML 관련)

### Medium
- **OpenAI API 비용**: 100+ 쿼리 실행 시 과금
  - **완화**: 샘플 크기 조정 (10-20 쿼리)

### Low
- **Qdrant 성능**: 로컬 벡터 DB 속도
  - **완화**: 프로덕션 환경 별도 측정

## Next
**PLAN.md** 작성 → 벤치마크 실행 계획, 샘플 데이터 준비, 성공 기준
