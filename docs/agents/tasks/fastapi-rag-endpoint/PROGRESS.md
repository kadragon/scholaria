# FastAPI RAG 엔드포인트 전환 진행 상황

## Summary
Django AskQuestionView를 FastAPI로 전환 (Phase 3)

## Goal & Approach
- **목표**: POST /api/rag/ask 엔드포인트 구현
- **전략**: 최소 변경 (Option A) - Django cache → Redis, OpenAI → AsyncOpenAI
- **방법**: TDD (테스트 우선)

## Completed Steps
- [x] **Step 1: 테스트 작성** (Red)
  - `api/tests/test_rag_endpoint.py` 생성 (7개 테스트)
  - 성공 케이스, 검증, 캐싱, 빈 결과 모두 커버
- [x] **Step 2: 스키마 작성** (Green)
  - `api/schemas/rag.py` 생성
  - QuestionRequest (topic_id, question validation)
  - AnswerResponse, Citation
- [x] **Step 3: Redis 의존성** (Green)
  - redis[hiredis] 설치
  - `api/dependencies/redis.py` 생성
  - `api/config.py`에 redis_url 추가
- [x] **Step 4: RAG Service 포팅** (Green)
  - `api/services/rag_service.py` 생성 (AsyncRAGService)
  - Django cache → redis.asyncio (set/get with JSON)
  - OpenAI → AsyncOpenAI
  - **핵심 수정**: sync_to_async로 EmbeddingService, QdrantService, RerankingService 래핑
- [x] **Step 5: 라우터 구현** (Green)
  - `api/routers/rag.py` 생성 (POST /api/rag/ask)
  - `api/main.py`에 라우터 등록
  - 에러 처리 (ValueError → 400, ConnectionError → 503, Exception → 500)
- [x] **Step 7: 검증 & 리팩터링** (Refactor)
  - 모든 7개 테스트 통과 (17.43초)
  - 기능 동등성 확인

## Current Failures
없음 (모든 테스트 통과)

## Decision Log
| 날짜 | 결정 | 근거 |
|------|------|------|
| 2025-09-30 | Option A (최소 변경) 선택 | 빠른 전환, 로직 변경 최소화, 점진적 최적화 가능 |
| 2025-09-30 | Redis direct (aioredis) | Django cache 의존성 제거, 비동기 네이티브 |
| 2025-09-30 | AsyncOpenAI 사용 | 공식 지원, 동기 버전과 API 동일 |

## Next Step
**태스크 완료 - Phase 3 완료 처리**
- TASKS.md 업데이트
- PLAN.md (django-to-fastapi-migration) 업데이트
- PROGRESS.md (django-to-fastapi-migration) 업데이트
- Phase 4 준비 (Write API 전환)
