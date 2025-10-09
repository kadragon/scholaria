# FastAPI RAG 엔드포인트 전환 계획

## Objective
Django `AskQuestionView` → FastAPI `POST /api/rag/ask` 전환 (Phase 3)

## Constraints
- TDD 원칙 (테스트 우선)
- 기존 RAG 로직 보존 (동작 동등성)
- 최소 변경 전략 (Option A)
- 모든 기존 테스트 통과 유지

## Target Files & Changes

### 1. Pydantic Schemas (`api/schemas/rag.py`)
- `QuestionRequest`: topic_id, question
- `AnswerResponse`: answer, citations, topic_id
- `Citation`: title, content, score, context_type, context_item_id

### 2. Dependencies (`api/dependencies/redis.py`)
- Redis 클라이언트 초기화 (`redis.asyncio`)
- `get_redis()` 의존성 함수

### 3. Rate Limiting (`api/dependencies/rate_limit.py`)
- slowapi 통합
- AnonRateThrottle 동등 (10/min)

### 4. RAG Service (`api/services/rag_service.py`)
- Django RAGService 복사 + 수정
- Django cache → aioredis
- OpenAI → AsyncOpenAI
- Django settings → Pydantic Settings

### 5. Router (`api/routers/rag.py`)
- POST /api/rag/ask
- 입력 검증 (Pydantic)
- 에러 처리 (400, 503, 500)
- Rate Limiting

### 6. Tests (`api/tests/test_rag_endpoint.py`)
- 성공 케이스 (질문 → 답변 + 인용)
- 캐싱 동작 확인
- 에러 처리 (빈 query, 빈 topic_ids, 서비스 장애)
- Django endpoint 응답 비교

## Test/Validation Cases

### Unit Tests
- [ ] QuestionRequest 스키마 검증
- [ ] AnswerResponse 스키마 직렬화
- [ ] Redis 캐싱 동작 (set/get)
- [ ] RAGService.query() 호출 성공

### Integration Tests
- [ ] POST /api/rag/ask 성공 (200)
- [ ] 캐시 히트 (두 번째 요청 빠름)
- [ ] 잘못된 입력 (400)
- [ ] OpenAI 장애 시 (503)
- [ ] Django vs FastAPI 응답 동등성

### Edge Cases
- [ ] 빈 search_results (답변: "no relevant info")
- [ ] topic_ids 존재하지 않음
- [ ] Rate limiting 초과 (429)

## Steps

### Step 1: 테스트 작성 (Red)
- [ ] `api/tests/test_rag_endpoint.py` 생성
- [ ] 기본 POST /api/rag/ask 테스트 (실패 예상)
- [ ] 에러 케이스 테스트

### Step 2: 스키마 작성 (Green)
- [ ] `api/schemas/rag.py` 생성
- [ ] QuestionRequest, AnswerResponse, Citation

### Step 3: Redis 의존성 (Green)
- [ ] `pyproject.toml`: redis[hiredis] 추가
- [ ] `api/dependencies/redis.py` 생성
- [ ] Redis 클라이언트 초기화

### Step 4: RAG Service 포팅 (Green)
- [ ] `api/services/rag_service.py` 생성
- [ ] Django cache → aioredis 변경
- [ ] OpenAI → AsyncOpenAI 변경
- [ ] Django settings → api.config 사용

### Step 5: 라우터 구현 (Green)
- [ ] `api/routers/rag.py` 생성
- [ ] POST /api/rag/ask 엔드포인트
- [ ] 에러 처리 (try/except)
- [ ] `api/main.py`에 라우터 등록

### Step 6: Rate Limiting (Green)
- [ ] slowapi 설치
- [ ] Rate limit 적용 (10/min anonymous)

### Step 7: 검증 & 리팩터링 (Refactor)
- [ ] 모든 테스트 통과
- [ ] Django endpoint와 비교 테스트
- [ ] 코드 리뷰 (중복 제거, 명확성)

## Rollback
- FastAPI 라우터 제거 → Django endpoint 계속 사용
- DB 변경 없음 (조회만 수행)
- Redis 추가는 선택사항 (Django cache 병행 가능)

## Review Hotspots

### 주의 필요
1. **OpenAI AsyncOpenAI**: 공식 지원 확인, API 호환성
2. **aioredis**: Django cache API와 다름 (set/get 시그니처)
3. **에러 처리**: Django의 3가지 예외 (ValueError, ConnectionError, Exception) 모두 처리
4. **캐싱 TTL**: Django는 900초, Redis도 동일하게

### 성능
- 첫 요청: Django와 동일 (RAG 로직 같음)
- 캐시 히트: Redis 더 빠를 수 있음 (직접 연결)

## Risks

### High
- **OpenAI API 호환성**: AsyncOpenAI가 동기 버전과 동일한 응답 보장해야 함

### Medium
- **캐싱 로직**: aioredis 사용법 다름 → 세심한 테스트 필요
- **Rate limiting**: slowapi 설정 오류 시 무제한 요청 가능

### Low
- RAGService 내부 로직 (이미 검증됨, 복사만)

## Status

- [x] Step 1: 테스트 작성 ✅ 완료 (7개 테스트)
- [x] Step 2: 스키마 작성 ✅ 완료 (QuestionRequest, AnswerResponse, Citation)
- [x] Step 3: Redis 의존성 ✅ 완료 (redis.asyncio, get_redis())
- [x] Step 4: RAG Service 포팅 ✅ 완료 (AsyncRAGService, sync_to_async)
- [x] Step 5: 라우터 구현 ✅ 완료 (POST /api/rag/ask)
- [ ] Step 6: Rate Limiting (향후 추가)
- [x] Step 7: 검증 & 리팩터링 ✅ 완료 (모든 테스트 통과)

### 구현 완료
- POST /api/rag/ask 엔드포인트 동작
- Redis 캐싱 동작 (900초 TTL)
- OpenAI AsyncOpenAI 사용
- Django ORM 호출 sync_to_async로 래핑
- 에러 처리 (400, 503, 500)
- 7개 테스트 모두 통과

### Rate Limiting 미구현
- slowapi 설치 및 적용은 Phase 3 완료 후 별도 작업으로 진행
- 현재 Django와 동일하게 무제한 (테스트 환경)
