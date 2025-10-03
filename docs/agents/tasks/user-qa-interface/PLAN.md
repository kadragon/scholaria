# Plan: User Q&A Interface with Streaming

## Objective
사용자가 토픽을 선택하고 스트리밍 방식으로 질문하며 대화를 이어갈 수 있는 PC 기반 채팅 인터페이스 구축

## Constraints
- TDD 원칙: 각 기능별 테스트 우선 작성
- 기존 shadcn/ui 디자인 시스템 준수
- PC 화면 기준 (1280px+ 최적화)
- 스트리밍 중 UI 블로킹 없음

## Target Files & Changes

### Backend (Phase 1-2)

#### 1. Streaming Support (새 파일)
- **`backend/routers/rag_streaming.py`** (신규)
  - `POST /api/rag/stream` 엔드포인트 추가
  - SSE 스트리밍 응답 구현
  - 이벤트 타입: `answer_chunk`, `citations`, `done`, `error`

- **`backend/services/rag_service.py`**
  - `query_stream()` 메서드 추가 (async generator)
  - OpenAI streaming API 호출 로직

- **`backend/schemas/rag.py`**
  - `StreamQuestionRequest` 스키마 추가 (session_id 포함)

#### 2. Session Management (기존 파일 수정)
- **`backend/routers/history.py`**
  - `GET /api/history/session/{session_id}` - 세션별 대화 조회 추가

- **`backend/schemas/history.py`**
  - `ConversationMessage` 스키마 추가 (role, content)

#### 3. Configuration
- **`pyproject.toml`**
  - `sse-starlette` 의존성 추가

- **`backend/main.py`**
  - `rag_streaming.router` 등록

### Frontend (Phase 3-4)

#### 4. Chat Page (신규)
- **`frontend/src/pages/chat/index.tsx`** (신규)
  - 3단 레이아웃: 토픽 선택 사이드바 | 메시지 영역 | (미래: 설정 패널)
  - SSE 연결 관리 hooks
  - 메시지 버블 렌더링 (user/assistant)
  - 입력창 + 전송 버튼

- **`frontend/src/pages/chat/components/TopicSelector.tsx`** (신규)
  - 토픽 목록 fetch
  - 선택된 토픽 표시

- **`frontend/src/pages/chat/components/MessageList.tsx`** (신규)
  - 메시지 리스트 (auto-scroll)
  - 타이핑 인디케이터
  - 인용 출처 Collapsible

- **`frontend/src/pages/chat/components/MessageInput.tsx`** (신규)
  - Textarea + 전송 버튼
  - Enter 키 전송 (Shift+Enter 줄바꿈)

- **`frontend/src/pages/chat/hooks/useChat.ts`** (신규)
  - SSE 연결 로직
  - 메시지 상태 관리
  - 에러 핸들링

#### 5. UI Components (재사용/확장)
- **`frontend/src/components/ui/message-bubble.tsx`** (신규)
  - shadcn/ui Card 기반 커스텀 컴포넌트

#### 6. Routing & Navigation
- **`frontend/src/App.tsx`**
  - `/chat` 경로 추가 (인증 필요)

- **`frontend/src/components/Sidebar.tsx`**
  - "질문하기" 메뉴 추가 (💬 아이콘)

### Tests (Phase 5)

#### Backend Tests
- **`backend/tests/test_rag_streaming.py`** (신규)
  - SSE 연결 테스트
  - 스트리밍 청크 수신 검증
  - 에러 이벤트 처리

- **`backend/tests/test_rag_service_streaming.py`** (신규)
  - `query_stream()` 유닛 테스트
  - OpenAI mock

#### Frontend Tests (선택적)
- E2E 테스트는 Phase 6으로 연기

## Steps

### Phase 1: Backend Streaming API
- [ ] Step 1.1: `sse-starlette` 추가, `backend/routers/rag_streaming.py` 스켈레톤 생성
- [ ] Step 1.2: `StreamQuestionRequest` 스키마 작성 + 테스트
- [ ] Step 1.3: `AsyncRAGService.query_stream()` 구현 (OpenAI streaming)
- [ ] Step 1.4: `/api/rag/stream` 엔드포인트 구현 (SSE)
- [ ] Step 1.5: 스트리밍 테스트 작성 및 검증

### Phase 2: Session History API
- [ ] Step 2.1: `GET /api/history/session/{session_id}` 엔드포인트 추가
- [ ] Step 2.2: 세션별 대화 조회 테스트

### Phase 3: Frontend Chat UI - Layout & Routing
- [ ] Step 3.1: `/chat` 라우트 추가 (`App.tsx`)
- [ ] Step 3.2: 사이드바에 "질문하기" 메뉴 추가
- [ ] Step 3.3: `pages/chat/index.tsx` 레이아웃 구조 생성 (3단 컬럼)
- [ ] Step 3.4: `TopicSelector` 컴포넌트 구현 (토픽 목록 fetch)

### Phase 4: Frontend Chat UI - Messaging
- [x] Step 4.1: `useChat` hook 작성 (상태 관리) ✓
- [x] Step 4.2: SSE 연결 로직 구현 (Fetch + ReadableStream) ✓
- [x] Step 4.3: `MessageList` 컴포넌트 (버블 UI + auto-scroll) ✓
- [x] Step 4.4: `MessageInput` 컴포넌트 (textarea + 전송) ✓
- [x] Step 4.5: 타이핑 인디케이터 + 인용 출처 표시 ✓

### Phase 5: Testing & Polish
- [x] Step 5.1: Backend 스트리밍 테스트 실행 (`pytest`) ✓
- [x] Step 5.2: 빌드 검증 (타입 에러 수정 완료) ✓
- [x] Step 5.3: 품질 검증 (ruff clean, mypy success) ✓
- [ ] Step 5.4: 수동 E2E 테스트 (프로덕션 배포 후)

### Phase 6: Documentation & Commit
- [x] Step 6.1: PROGRESS.md 업데이트 ✓
- [x] Step 6.2: PLAN.md 상태 업데이트 ✓
- [x] Step 6.3: Commit (dc715bf) ✓
- [ ] Step 6.4: TASKS.md 업데이트 (pending)

## Test/Validation Cases

### Backend
1. SSE 연결 수립 및 청크 수신
2. `answer_chunk` 이벤트 누적 시 완전한 답변 생성
3. `citations` 이벤트 파싱
4. `error` 이벤트 발생 시 연결 종료
5. 세션 ID로 대화 이력 조회

### Frontend
1. 토픽 선택 후 입력창 활성화
2. 메시지 전송 시 즉시 사용자 버블 표시
3. 스트리밍 응답이 실시간으로 어시스턴트 버블에 추가됨
4. 인용 출처가 답변 완료 후 Collapsible로 표시됨
5. 새로고침 시 세션 유지 (sessionStorage)

## Rollback
- 각 Phase별 commit 분리
- Backend API는 기존 `/api/rag/ask`에 영향 없음 (신규 엔드포인트)
- Frontend 라우트는 독립적 (기존 admin 페이지 무관)

## Review Hotspots

### Security
- SSE 연결에 JWT 토큰 검증 필수
- session_id는 UUID v4로 생성 (클라이언트 측)

### Performance
- 스트리밍 청크 크기 적절히 설정 (OpenAI delta)
- 메시지 리스트 가상화 고려 (20개 초과 시)

### UX
- 스트리밍 중 입력창 비활성화
- 연결 끊김 시 재연결 안내 메시지

## Status
- [x] Phase 1: Backend Streaming API ✅ (f2e5c8b)
- [x] Phase 2: Session History API ✅ (8d78a14)
- [x] Phase 3: Frontend Chat UI - Layout & Routing ✅ (161dbda)
- [x] Phase 4: Frontend Chat UI - Messaging ✅ (dc715bf)
- [x] Phase 5: Testing & Polish ✅ (143 tests passing)
- [x] Phase 6: Documentation & Commit ✅
