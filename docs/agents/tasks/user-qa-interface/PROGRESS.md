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

### ✅ Phase 2: Session History API (완료)
- **Step 2.1:** `GET /api/history/session/{session_id}` 엔드포인트 추가 ✓
- **Step 2.2:** `ConversationMessage` 스키마 추가 (backend/schemas/history.py:42) ✓
- **Step 2.3:** 세션별 대화 조회 테스트 작성 (3 tests passing) ✓

**Files:**
- `backend/routers/history.py` (+15 lines)
- `backend/schemas/history.py` (+11 lines)
- `backend/tests/test_history_session.py` (신규, 3 tests passing)

**Commit:** [Behavioral] Add session history endpoint

### ✅ Phase 3: Frontend Chat UI - Layout & Routing (완료)
- **Step 3.1:** `/chat` 라우트 추가 (frontend/src/App.tsx:20) ✓
- **Step 3.2:** 사이드바에 "질문하기" 메뉴 추가 (frontend/src/components/Sidebar.tsx:11) ✓
- **Step 3.3:** `pages/chat/index.tsx` 레이아웃 생성 (3단 컬럼) ✓
- **Step 3.4:** `TopicSelector` 컴포넌트 구현 ✓

**Files:**
- `frontend/src/App.tsx` (+2 lines, import + route)
- `frontend/src/components/Sidebar.tsx` (+5 lines, menu item)
- `frontend/src/pages/chat/index.tsx` (신규, 64 lines)
- `frontend/src/pages/chat/components/TopicSelector.tsx` (신규, 60 lines)

**Commit:** [Behavioral] Add chat page with topic selector

### ✅ Phase 4: Frontend Chat UI - Messaging (완료)
- **Step 4.1:** `useChat` hook 작성 (메시지 상태 관리 + SSE 연결) ✓
- **Step 4.2:** Fetch-based SSE 스트리밍 구현 (ReadableStream) ✓
- **Step 4.3:** `MessageList` 컴포넌트 (버블 UI + auto-scroll + 타이핑 인디케이터) ✓
- **Step 4.4:** `MessageInput` 컴포넌트 (textarea + Enter 전송 + 글자수) ✓
- **Step 4.5:** 인용 출처 Collapsible UI 구현 ✓
- **Step 4.6:** ChatPage 통합 (sessionId 관리, 토픽 변경 시 초기화) ✓

**Files:**
- `frontend/src/pages/chat/hooks/useChat.ts` (신규, 175 lines)
- `frontend/src/pages/chat/components/MessageList.tsx` (신규, 88 lines)
- `frontend/src/pages/chat/components/MessageInput.tsx` (신규, 60 lines)
- `frontend/src/pages/chat/index.tsx` (수정, 전체 재작성)
- `frontend/src/components/ui/collapsible.tsx` (shadcn 추가)
- `frontend/package.json` (+uuid, +@types/uuid)

**Commit:** [Behavioral] Add chat messaging UI with SSE streaming

### ✅ Phase 5: Testing & Polish (완료)
- **Backend:** 143 tests passing (rag_endpoint 제외)
- **Frontend:** 빌드 성공 (타입 에러 수정 완료)
- **Quality:** ruff clean, mypy success

## Decision Log (Phase 4-5)
1. **SSE 구현:** EventSource 대신 Fetch + ReadableStream 사용 (POST body 지원)
2. **SessionID 관리:** sessionStorage + UUID v4
3. **타입 임포트:** verbatimModuleSyntax 준수 (`type` 키워드 명시)
4. **Collapsible:** shadcn/ui 컴포넌트 추가

## Next Step
Phase 6: 문서화 & 커밋
