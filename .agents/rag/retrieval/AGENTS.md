# RAG Retrieval Pipeline - Agent Knowledge Base

## Intent
임베딩 → 벡터 검색 → 리랭킹 → LLM 응답으로 이어지는 Scholaria RAG 파이프라인을 안정적으로 운용한다.

## Constraints
- **TDD Required**: Red → Green → Refactor 사이클로 서비스 레이어를 개발한다.
- **Service Isolation**: 임베딩·검색·리랭킹·LLM 호출은 모듈 단위로 테스트 가능해야 한다.
- **Mock Boundaries**: 외부 API는 부모 모듈 경로에서 import 하여 pytest에서 손쉽게 패치한다(`openai.OpenAI`, `openai.AsyncOpenAI` 등).
- **Type Safety**: mypy 통과 + TypedDict/Pydantic 스키마 준수.

## Context

### Core Services
1. **EmbeddingService** (`backend/retrieval/embeddings.py`)
   - OpenAI `text-embedding-3-large`, Redis 기반 `EmbeddingCache` 지원.
   - 배치 임베딩 지원, 모니터(`OpenAIUsageMonitor`)로 토큰·비용 추적.
2. **QdrantService** (`backend/retrieval/qdrant.py`)
   - 토픽 ID 필터링, 벡터 차원 3072, 검색 상한 기본 10.
3. **RerankingService** (`backend/retrieval/reranking.py`)
   - BGE reranker, 상위 5개(default) rerank.
4. **AsyncRAGService** (`backend/services/rag_service.py`)
   - 전체 파이프라인 오케스트레이션, Redis에 쿼리 결과 15분 캐시(빈 결과 5분), 스트리밍 API 포함.
5. **OpenAIUsageMonitor** (`backend/retrieval/monitoring.py`)
   - API 사용량, 비용 추정, rate-limit 감시.

### Flow
```
질문 → 임베딩 생성 → Qdrant 유사도 검색 → BGE 리랭크 → 컨텍스트 준비 → GPT-4o-mini 응답 → 응답/출처 반환
```

### Test Coverage (2025-10-09)
- 단위 테스트: `backend/tests/test_embedding_cache.py`, `test_rag_endpoint.py`, `test_rag_streaming.py`, `test_openai_usage_monitor` 관련 케이스.
- 통합 시나리오: Docker Compose 환경에서 Redis/Qdrant/PostgreSQL 의존성을 활성화하여 실행 (`DOCKER_INTEGRATION_TESTS=true`).
- Mock 사례: OpenAI/Redis/Qdrant 클라이언트는 pytest에서 monkeypatch 또는 fixture로 교체한다.

## Changelog

### 2025-10-09
- Redis 쿼리 캐시 TTL(15분/5분)과 AsyncOpenAI 기반 스트리밍 동작을 문서에 반영.
- 테스트 포커스를 `backend/tests` 경로로 업데이트하고 외부 `rag/tests` 참조 제거.
- OpenAIUsageMonitor가 비용 추정과 rate-limit 감시를 담당함을 명시.
