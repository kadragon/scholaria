# Research: Golden Dataset Integration Testing

## Goal
Golden Dataset을 활용한 실제 Qdrant 벡터 검색 통합 테스트 및 관련 인용 정확도 80% 검증 구현

## Scope
- 기존 mock 기반 `test_golden_accuracy.py` → 실제 Qdrant 호출로 전환
- `test_performance_benchmark.py` Mock 기반 성능 측정 유지
- Redis + Qdrant 통합 환경에서 실행 가능한 테스트 작성

## Related Files

### 테스트 관련
- `backend/tests/test_golden_accuracy.py` — 현재 mock 기반 lexical similarity 사용 (FAKE_CONTEXTS)
- `backend/tests/test_performance_benchmark.py` — Mock 기반 응답 지연 측정, 유지 가능
- `backend/tests/fixtures/golden_dataset.json` — 5개 Q&A 샘플 (expected_context_ids 포함)
- `backend/tests/conftest.py` — `golden_dataset` fixture 정의됨, DB session/admin fixtures 제공

### 서비스 레이어
- `backend/services/rag_service.py:79-149` — `AsyncRAGService.query()` 전체 파이프라인
  - embed(query) → Qdrant search → rerank → LLM answer
  - Redis 캐시 적용 (900초 TTL)
- `backend/retrieval/qdrant.py:154-215` — `QdrantService.search_similar()` (topic 필터링 + 벡터 검색)
- `backend/retrieval/reranking.py:17-63` — `RerankingService.rerank_results()` (BGE cross-encoder)
- `backend/retrieval/embeddings.py` — OpenAI embedding 생성 (Redis 캐시 사용)

## Hypotheses

1. **Golden dataset 인프라는 이미 구축됨** — `conftest.py`에 fixture 존재, JSON 형식 검증됨
2. **Mock 기반 테스트는 정확도를 시뮬레이션** — FAKE_CONTEXTS + lexical similarity로 80% 정확도 달성
3. **실제 Qdrant 검색 시나리오 필요** — 프로덕션 환경에서 벡터 검색·리랭킹 품질 검증 불가능
4. **통합 테스트는 Redis + Qdrant 서비스 필요** — `docker-compose.dev.yml` 환경에서 실행 가능
5. **Expected context IDs는 실제 DB에 존재해야 함** — SQLAlchemy + Qdrant 양쪽 데이터 동기화 필요

## Evidence

### 현재 구현 상태
- `test_golden_accuracy.py` — 3개 테스트, **mock 기반**, 실제 DB/Qdrant 사용 안 함
  - `simulate_search()` — BASELINE_ORDERS로 검색 순서 시뮬레이션
  - `rerank_results()` — lexical similarity로 리랭킹 시뮬레이션
  - 테스트: dataset 로드, 80% 정확도, 리랭킹 개선(+0.10)
- `test_performance_benchmark.py` — 3개 테스트, **mock 기반**, 응답 시간 측정
  - AsyncRAGService의 모든 메서드 mock (embed/search/rerank/answer)
  - 실패 시나리오 없음 (외부 서비스 의존성 차단)

### Golden Dataset 구조
```json
{
  "question": "What is the school's admission policy?",
  "expected_context_ids": [1, 3],  // ContextItem.id
  "topic_id": 1,
  "difficulty": "easy",
  "notes": "Direct match with admission FAQ context"
}
```

### 실제 RAG 파이프라인 (AsyncRAGService)
1. **Embedding** — `embeddings.generate_embedding(query)` → OpenAI API (Redis 캐시)
2. **Search** — `qdrant.search_similar(embedding, topic_ids, limit=10)` → Qdrant 벡터 검색
3. **Rerank** — `reranking.rerank_results(query, results, top_k=5)` → BGE reranker
4. **Answer** — `_generate_answer(query, context)` → AsyncOpenAI chat completion

### 데이터 동기화 요구사항
- **SQLAlchemy** — Topic, Context, ContextItem 모델 (테스트 DB에 생성 필요)
- **Qdrant** — ContextItem 임베딩 저장 (collection: `context_items`, vector_size: 1536)
- **expected_context_ids** — Golden dataset의 ID가 실제 ContextItem과 매칭되어야 검증 가능

## Assumptions / Open Questions

### Assumptions
- Qdrant 서비스는 `docker-compose.dev.yml`로 기동 가능 (host: qdrant, port: 6333)
- Redis 서비스는 캐시 공유용으로 이미 구성됨 (host: redis, port: 6379)
- OpenAI API 키는 테스트 환경에서 사용 가능 (또는 mock 가능)
- Golden dataset은 **정적 fixture**이므로 테스트 전 DB/Qdrant 시딩 필요

### Open Questions
1. **ContextItem 시딩 전략** — 5개 질문에 대응하는 실제 문서를 어떻게 생성할 것인가?
   - Option A: Fixture로 SQL + Qdrant 수동 삽입 (정확도 제어 가능)
   - Option B: 간단한 샘플 문서 생성 → 인제스션 파이프라인으로 임베딩 자동 생성
2. **통합 테스트 격리** — 전체 테스트 스위트와 분리 필요한가?
   - `@pytest.mark.integration` 마커 사용 → CI에서 Redis/Qdrant 필수
   - 로컬에서는 `--skip-integration` 옵션으로 제외 가능
3. **OpenAI API 호출 제어** — 임베딩/LLM 호출을 테스트마다 실행할 것인가?
   - Embedding: 캐시 활용 또는 fixture로 사전 생성 (비용 절감)
   - LLM answer: Mock 유지 (품질 검증은 별도 manual QA)
4. **정확도 기준점** — Mock 기반 80%를 실제 벡터 검색에서도 달성 가능한가?
   - 샘플 데이터 품질에 따라 달라질 수 있음 (초기 목표: ≥60%, 개선 목표: ≥80%)

## Risks

1. **External API 의존** — OpenAI embedding 호출 시 네트워크/비용/레이트 제한 발생 가능
2. **Docker 환경 필수** — CI/로컬 환경에서 Qdrant/Redis 서비스 기동 실패 시 테스트 불가
3. **데이터 품질** — Golden dataset의 expected_context_ids가 실제 검색 결과와 불일치 시 False Negative
4. **테스트 속도** — 실제 임베딩 생성 시 5개 질문 × 임베딩 시간 = 수 초 소요 (캐시 필수)

## Next Steps
1. **Plan 작성** — 시딩 전략, 테스트 격리, OpenAI Mock 범위 결정
2. **Fixture 설계** — Topic/Context/ContextItem 샘플 데이터 + Qdrant 임베딩 삽입
3. **통합 테스트 작성** — 실제 `AsyncRAGService.query()` 호출 + 정확도 검증
4. **CI 통합** — GitHub Actions에 Redis/Qdrant 서비스 추가 (또는 skip 옵션)
