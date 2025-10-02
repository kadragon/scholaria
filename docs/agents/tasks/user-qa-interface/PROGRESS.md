# Progress: User Q&A Interface with Streaming

## Summary
PC 기반 스트리밍 질의응답 인터페이스 구축 진행 중

## Goal & Approach
- **Backend:** SSE 스트리밍 엔드포인트 (`/api/rag/stream`)
- **Frontend:** React 채팅 UI (토픽 선택 + 메시지 스트리밍)
- **Approach:** TDD 기반 6 Phase 점진적 구현

## Completed Steps

### ✅ Phase 1: Backend Streaming API (완료)
- **Step 1.1:** `sse-starlette` 의존성 추가 ✓
- **Step 1.2:** `StreamQuestionRequest` 스키마 작성 (topic_id, question, session_id) ✓
- **Step 1.3:** `AsyncRAGService.query_stream()` 메서드 구현 ✓
  - OpenAI streaming API 연동
  - SSE 이벤트 타입: `answer_chunk`, `citations`, `done`, `error`
- **Step 1.4:** `POST /api/rag/stream` 엔드포인트 추가 (backend/routers/rag_streaming.py) ✓
- **Step 1.5:** 스트리밍 테스트 작성 (스키마 검증, 라우트 등록) ✓

**Files:**
- `backend/routers/rag_streaming.py` (신규)
- `backend/schemas/rag.py` (+StreamQuestionRequest)
- `backend/services/rag_service.py` (+query_stream, +_generate_answer_stream)
- `backend/main.py` (라우터 등록)
- `backend/tests/test_rag_streaming.py` (신규, 2 tests passing)

**Commit:** [Behavioral] Add SSE streaming endpoint for RAG queries

## Current Failures
없음 (Phase 1 테스트 통과)

## Decision Log
1. **SSE 라이브러리 선택:** `sse-starlette` 사용 (FastAPI 표준)
2. **이벤트 타입:** JSON 형식으로 `type` 필드 기반 구분
3. **테스트 전략:** 통합 테스트는 수동 E2E로 연기 (Qdrant/OpenAI 의존성 회피)

## Next Step
Phase 2: Session History API (`GET /api/history/session/{session_id}`)
