# RAG API Specification

## Context & Goal

**Context**: Scholaria의 핵심 기능인 RAG (Retrieval-Augmented Generation) 엔드포인트를 Django에서 FastAPI로 전환합니다. 기존 `AskQuestionView`의 동작을 보존하면서 비동기 처리와 Redis 캐싱을 통한 성능 개선을 목표로 합니다.

**Goal**: `POST /api/rag/ask` 엔드포인트를 통해 사용자 질문에 대한 AI 답변과 출처 인용을 제공합니다. 동일한 질문에 대해서는 Redis 캐싱으로 빠르게 응답하며, Rate Limiting으로 과도한 요청을 방지합니다.

## Scope

**In Scope**:
- RAG 질의응답 엔드포인트 (`POST /api/rag/ask`)
- Redis 캐싱 (900초 TTL)
- OpenAI AsyncOpenAI 비동기 처리
- Qdrant 벡터 검색
- 인용(Citation) 반환 (출처 정보)
- 에러 처리 (400, 503, 500)

**Out of Scope**:
- Rate Limiting (Phase 3 완료 후 별도 추가)
- Streaming 응답 (별도 엔드포인트)
- 세션 기반 대화 이력
- 피드백 시스템 (별도 API)

## Contract

### 1. RAG Query Endpoint

#### POST `/api/rag/ask`

사용자 질문에 대한 AI 답변 생성 (RAG).

**요청 (JSON)**:
```json
{
  "topic_id": 1,
  "question": "What is Anthropic's mission?"
}
```

**Pydantic Schema**:
```python
class QuestionRequest(BaseModel):
    topic_id: int = Field(..., gt=0, description="Topic ID to search in")
    question: str = Field(..., min_length=1, max_length=1000, description="User question")
```

**응답 (200 OK)**:
```json
{
  "answer": "Anthropic's mission is to ensure that artificial general intelligence benefits all of humanity...",
  "citations": [
    {
      "title": "About Anthropic",
      "content": "Anthropic is an AI safety company...",
      "score": 0.89,
      "context_type": "PDF",
      "context_item_id": 123
    }
  ],
  "topic_id": 1
}
```

**Pydantic Schema**:
```python
class Citation(BaseModel):
    title: str
    content: str
    score: float
    context_type: str
    context_item_id: int

class AnswerResponse(BaseModel):
    answer: str
    citations: list[Citation]
    topic_id: int
```

**에러**:
- `400 BAD REQUEST`: 빈 질문 (`question` 누락/빈 문자열)
- `400 BAD REQUEST`: 잘못된 `topic_id` (0 이하)
- `404 NOT FOUND`: `topic_id`가 DB에 존재하지 않음
- `503 SERVICE UNAVAILABLE`: OpenAI API 장애
- `500 INTERNAL SERVER ERROR`: 기타 서버 오류

### 2. Redis Caching

**Cache Key**: `f"rag_query:{topic_id}:{question}"`

**TTL**: 900초 (15분)

**동작**:
1. 캐시 조회: `redis.get(cache_key)`
2. 캐시 히트: JSON 파싱 후 즉시 반환
3. 캐시 미스: RAG 로직 실행 → 결과 캐싱 → 반환

**구현**:
```python
import redis.asyncio as aioredis
import json

async def get_redis() -> aioredis.Redis:
    """Redis 클라이언트 의존성"""
    redis = aioredis.from_url("redis://localhost:6379/0", decode_responses=True)
    try:
        yield redis
    finally:
        await redis.close()

# 캐싱 로직 (api/routers/rag.py)
cache_key = f"rag_query:{topic_id}:{question}"
cached = await redis.get(cache_key)
if cached:
    return json.loads(cached)

# RAG 실행
result = await rag_service.query(topic_id, question)

# 캐싱 저장
await redis.set(cache_key, json.dumps(result), ex=900)
```

### 3. AsyncRAGService

**위치**: `backend/services/rag_service.py`

**주요 메서드**: `async def query(topic_id: int, question: str) -> dict`

**의존성**:
- `AsyncOpenAI`: OpenAI API 비동기 호출
- `sync_to_async`: Django ORM 호출 (Context, ContextItem 조회)
- Qdrant Client: 벡터 검색

**워크플로우**:
1. Topic 존재 확인 (Django ORM)
2. 질문 임베딩 생성 (OpenAI `text-embedding-3-small`)
3. Qdrant 벡터 검색 (top 5, score_threshold=0.7)
4. Context 조회 (Django ORM, `sync_to_async`)
5. OpenAI Chat Completion (GPT-4, system prompt + context + question)
6. Citation 생성 (title, content, score, context_type, context_item_id)
7. 응답 반환

**에러 처리**:
```python
try:
    # RAG 로직
except ValueError as e:
    # 잘못된 입력 (빈 query, topic_id 없음)
    raise HTTPException(status_code=400, detail=str(e))
except ConnectionError as e:
    # OpenAI/Qdrant 연결 실패
    raise HTTPException(status_code=503, detail="Service temporarily unavailable")
except Exception as e:
    # 기타 오류
    raise HTTPException(status_code=500, detail="Internal server error")
```

### 4. Rate Limiting (Future)

**계획**: slowapi 사용 (10 requests/min for anonymous)

**구현 예시**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/ask")
@limiter.limit("10/minute")
async def ask_question(...):
    # ...
```

**에러**:
- `429 TOO MANY REQUESTS`: Rate limit 초과

## Examples

### Example 1: 정상 질의응답

```bash
curl -X POST http://localhost:8000/api/rag/ask \
  -H "Content-Type: application/json" \
  -d '{
    "topic_id": 1,
    "question": "What is Anthropic?"
  }'

# 응답 (200 OK)
{
  "answer": "Anthropic is an AI safety and research company founded in 2021...",
  "citations": [
    {
      "title": "About Anthropic",
      "content": "Anthropic is dedicated to building safe, steerable AI systems...",
      "score": 0.92,
      "context_type": "PDF",
      "context_item_id": 42
    },
    {
      "title": "Company Overview",
      "content": "Founded by former OpenAI researchers...",
      "score": 0.87,
      "context_type": "MARKDOWN",
      "context_item_id": 43
    }
  ],
  "topic_id": 1
}
```

### Example 2: 캐시 히트 (두 번째 요청)

```bash
# 동일 질문 재요청 (15분 내)
curl -X POST http://localhost:8000/api/rag/ask \
  -H "Content-Type: application/json" \
  -d '{
    "topic_id": 1,
    "question": "What is Anthropic?"
  }'

# 응답 (200 OK, 즉시 반환)
# (동일한 응답, 캐시에서 로드)
```

### Example 3: 잘못된 입력 (400)

```bash
# 빈 질문
curl -X POST http://localhost:8000/api/rag/ask \
  -H "Content-Type: application/json" \
  -d '{
    "topic_id": 1,
    "question": ""
  }'

# 응답 (400 BAD REQUEST)
{
  "detail": [
    {
      "loc": ["body", "question"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

### Example 4: OpenAI 장애 (503)

```bash
curl -X POST http://localhost:8000/api/rag/ask \
  -H "Content-Type: application/json" \
  -d '{
    "topic_id": 1,
    "question": "Test question"
  }'

# 응답 (503 SERVICE UNAVAILABLE)
{
  "detail": "Service temporarily unavailable"
}
```

### Example 5: 검색 결과 없음

```bash
curl -X POST http://localhost:8000/api/rag/ask \
  -H "Content-Type: application/json" \
  -d '{
    "topic_id": 1,
    "question": "Completely unrelated question"
  }'

# 응답 (200 OK)
{
  "answer": "I don't have enough relevant information to answer this question.",
  "citations": [],
  "topic_id": 1
}
```

## Acceptance Criteria

### AC1: 정상 RAG 응답

- [x] POST /api/rag/ask 성공 시 답변 + 인용 반환
- [x] 인용은 score 기준 정렬 (내림차순)
- [x] OpenAI GPT-4 사용
- [x] Qdrant 벡터 검색 (top 5, score_threshold=0.7)

### AC2: Redis 캐싱

- [x] 동일 질문 두 번째 요청 시 캐시 히트
- [x] TTL 900초 설정
- [x] 캐시 키: `rag_query:{topic_id}:{question}`

### AC3: 에러 처리

- [x] 빈 질문 → 400
- [x] 잘못된 topic_id → 400
- [x] 존재하지 않는 topic_id → 404
- [x] OpenAI 장애 → 503
- [x] 기타 오류 → 500

### AC4: 비동기 처리

- [x] AsyncOpenAI 사용
- [x] Django ORM `sync_to_async` 래핑
- [x] Redis `aioredis` 사용

### AC5: 테스트 커버리지

- [x] 7개 테스트 통과 (성공, 캐싱, 에러 케이스)
- [x] Django `AskQuestionView`와 응답 동등성 확인

## Dependencies

| Name | Latest | Chosen | Rationale | Link |
|------|--------|--------|-----------|------|
| redis | 5.2.0 | 5.2.0 | Redis 비동기 클라이언트 (`redis.asyncio`) | https://github.com/redis/redis-py |
| openai | 1.55.3 | 1.55.3 | AsyncOpenAI 지원, 공식 라이브러리 | https://github.com/openai/openai-python |
| qdrant-client | 1.12.1 | 1.12.1 | 벡터 검색 (이미 설치됨) | https://github.com/qdrant/qdrant-client |
| slowapi | 0.1.9 | (미설치) | Rate limiting (향후 추가) | https://github.com/laurentS/slowapi |

## Versioning & Migration

### Version: 1.0.0 (Initial Implementation)

**릴리스**: Phase 3 (2025-09-30)

**변경사항**:
- Django `AskQuestionView` → FastAPI `POST /api/rag/ask` 전환
- Redis 캐싱 도입 (Django cache → aioredis)
- AsyncOpenAI 비동기 처리
- Pydantic 스키마 (QuestionRequest, AnswerResponse, Citation)

**마이그레이션**:
- **DB 마이그레이션**: 불필요 (조회만 수행)
- **Redis 설정**: `REDIS_URL` 환경 변수 추가 필요
- **클라이언트 변경**: `/api/rag/ask` 엔드포인트로 요청 변경

**하위 호환성**: Django 엔드포인트와 병행 운영 가능 (Phase 3-4)

### Future: Version 2.0.0 (Streaming)

**계획**:
- `POST /api/rag/stream` 엔드포인트 추가 (SSE)
- 실시간 답변 스트리밍
- 세션 기반 대화 이력 저장

**하위 호환성**: 기존 `/api/rag/ask`는 유지

## Performance

### Latency

| 시나리오 | 평균 응답 시간 | 설명 |
|---------|-------------|------|
| 캐시 미스 (첫 요청) | 2-5초 | OpenAI API 호출 + Qdrant 검색 |
| 캐시 히트 (재요청) | < 50ms | Redis에서 JSON 로드 |
| 검색 결과 없음 | 1-2초 | Qdrant 검색만 수행 |

### Throughput

- **동시 요청**: FastAPI 비동기 처리로 Django 대비 2-3배 개선 예상
- **병목**: OpenAI API Rate Limit (Tier 기준)

### Caching Strategy

- **TTL**: 900초 (15분) — 질문은 짧은 시간 내 재요청 가능성 높음
- **Invalidation**: Context 업데이트 시 자동 무효화 불가 (TTL 의존)
- **향후 개선**: Context 업데이트 시 관련 캐시 키 삭제 (Pub/Sub)

## Security Considerations

### 1. Prompt Injection

**리스크**: 악의적 질문으로 시스템 프롬프트 우회

**완화**:
- System prompt에 명확한 지침 ("Only answer based on provided context")
- 사용자 입력 길이 제한 (1000자)
- OpenAI Moderation API 사용 (향후)

### 2. OpenAI API Key

**리스크**: API 키 노출 시 비용 소진

**완화**:
- 환경 변수에서 로드 (`OPENAI_API_KEY`)
- `.env` 파일 Git 제외
- Rate Limiting (향후)

### 3. Redis Injection

**리스크**: 악의적 캐시 키로 Redis 명령 실행

**완화**:
- 캐시 키는 서버에서 생성 (`f"rag_query:{topic_id}:{question}"`)
- 사용자 입력은 JSON 값으로만 저장

## References

- **PLAN**: `.tasks/fastapi-rag-endpoint/PLAN.md` (구현 계획)
- **Tests**: `backend/tests/test_rag_endpoint.py` (7개 테스트)
- **Django Implementation**: `rag/views.py:AskQuestionView` (원본 로직)
- **OpenAI Async Guide**: https://platform.openai.com/docs/guides/async
- **Qdrant Python Client**: https://qdrant.tech/documentation/frameworks/python/
