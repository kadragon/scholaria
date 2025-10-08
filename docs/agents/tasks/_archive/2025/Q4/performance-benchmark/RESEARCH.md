# Research: Performance Benchmark

## Goal
프로덕션 환경 기준으로 RAG 시스템의 성능을 정량적으로 측정하고 검증합니다.

## Scope
- **관련 인용 정확도**: 검색된 context가 질문과 관련성 80% 이상
- **응답 지연**: E2E 응답 시간 3초 미만
- **동시 사용자 부하**: 병렬 요청 처리 안정성

## Related Files/Flows

### RAG Pipeline
- `backend/services/rag_service.py:79-177` - `AsyncRAGService.query()` 메인 파이프라인
  - Step 1: 임베딩 생성 (119-121)
  - Step 2: Qdrant 벡터 검색 (124-129)
  - Step 3: BGE Reranker 재순위 (143-148)
  - Step 4: 컨텍스트 준비 (151)
  - Step 5: OpenAI LLM 응답 생성 (154)
- `backend/routers/rag.py:51-119` - REST 엔드포인트
- `backend/routers/rag_streaming.py:41-59` - SSE 스트리밍 엔드포인트

### Performance-Critical Components
- `backend/retrieval/embeddings.py` - OpenAI 임베딩 생성 (캐시 지원)
- `backend/retrieval/qdrant.py` - 벡터 검색 (Qdrant 호출)
- `backend/retrieval/reranking.py` - BGE 재순위 모델 (CPU/GPU 바운드)
- `backend/retrieval/cache.py` - Redis 임베딩 캐시 (15분 TTL)

### Existing Tests
- `backend/tests/test_rag_endpoint.py` - 6개 단위 테스트 (mock 기반, 기능 검증)
- `backend/tests/test_rag_streaming.py` - 2개 스키마 테스트 (엔드포인트 등록 검증)
- **Missing:** 성능/부하/정확도 테스트 없음

## Hypotheses

### H1: 응답 지연 3초 미만 달성 가능
- **근거:** Redis 캐시 적중 시 임베딩 생성 생략 가능
- **검증:** E2E 타이머로 각 단계 측정

### H2: 관련 인용 80% 목표는 Golden Dataset 필요
- **근거:** 재순위 모델(BGE)이 이미 적용되어 있으나 정량 측정 필요
- **검증:** 수동 라벨링된 질문-컨텍스트 쌍으로 정확도 측정

### H3: 동시 사용자 부하는 AsyncIO 기반으로 확장 가능
- **근거:** `AsyncRAGService`와 Redis 공유 캐시 구조
- **검증:** locust/k6 또는 pytest-asyncio로 병렬 요청 시뮬레이션

## Evidence

### Current Setup
- Python 3.13 + asyncio native (`asyncio.to_thread` 사용)
- Redis 캐시: TTL 15분, 임베딩 TTL 30일
- Qdrant 벡터 DB: 검색 제한 10개, 재순위 상위 5개

### pytest Markers
`pytest.ini:13-14`에 성능 테스트 마커 정의됨:
```ini
markers =
    performance: marks tests as performance benchmarks
    golden: marks tests as golden dataset validation
```

### Config
- `backend/config.py:48-49` - `RAG_SEARCH_LIMIT=10`, `RAG_RERANK_TOP_K=5`
- 환경변수로 조정 가능

## Assumptions/Open Qs

### Assumptions
1. **Golden Dataset 부재**: 현재 프로덕션 데이터가 없으므로 샘플 데이터셋 생성 필요
2. **외부 API 의존**: OpenAI 호출 지연은 제어 불가 (mock으로 대체 필요)
3. **부하 테스트 인프라**: Docker Compose 환경에서 실행 가능

### Open Questions
1. **Golden Dataset 크기**: 몇 개의 질문-컨텍스트 쌍으로 신뢰 가능?
   - 제안: 최소 20-30개 (다양한 난이도, 토픽 분포)
2. **부하 테스트 대상**: 단일 엔드포인트 vs. 전체 파이프라인?
   - 제안: `/api/rag/ask` 엔드포인트 중심 (실제 사용 패턴)
3. **성능 임계값**: 3초는 P50, P95, P99 중 무엇?
   - 제안: P95 3초 미만 (대부분 요청 커버)
4. **부하 테스트 규모**: 동시 사용자 수 목표?
   - 제안: 10-50 동시 요청 (학교 규모 가정)

## Sub-agent Findings
N/A (Research 단계에서 직접 조사 완료)

## Risks
1. **OpenAI API 비용**: 대량 테스트 시 API 호출 증가
   - 완화: Mock 또는 캐시 적중 시나리오 우선
2. **Docker 환경 오버헤드**: 로컬 vs. 컨테이너 성능 차이
   - 완화: Docker Compose 기반 통합 테스트로 일관성 확보
3. **Golden Dataset 품질**: 수동 라벨링 오류 가능
   - 완화: 소규모 검증 후 점진적 확장

## Next
Plan 단계로 진행 - 테스트 파일 설계 및 구현 계획 수립
