# Research: User Q&A Interface with Streaming

## Goal
사용자 친화적인 질의응답 인터페이스 구축 - 토픽 선택, 스트리밍 답변, 대화 이력 유지

## Scope
- **Frontend:** React 기반 PC용 채팅 UI (shadcn/ui)
- **Backend:** SSE 스트리밍 엔드포인트 추가
- **Features:** 토픽 선택, 메시지 스트리밍, 대화 세션 관리, 인용 출처 표시

## Related Files/Flows

### Backend
- `backend/routers/rag.py:49` - 기존 `/api/rag/ask` 엔드포인트 (non-streaming)
- `backend/services/rag_service.py` - RAG 로직 (스트리밍 지원 필요)
- `backend/routers/history.py` - 히스토리 조회/피드백 API
- `backend/schemas/rag.py` - QuestionRequest, AnswerResponse 스키마

### Frontend
- `frontend/src/App.tsx` - 라우팅 (신규 `/chat` 경로 추가)
- `frontend/src/components/Sidebar.tsx` - 사이드바에 "질문하기" 메뉴 추가
- `frontend/src/providers/dataProvider.ts` - API 연동

### Infrastructure
- FastAPI SSE 지원: `sse-starlette` 라이브러리 추가 필요
- OpenAI streaming API 사용 가능 (기존 `openai` 패키지)

## Hypotheses

### H1: SSE 스트리밍 구현
- FastAPI는 `StreamingResponse` + `sse-starlette`로 SSE 지원
- OpenAI API는 `stream=True` 옵션으로 스트리밍 가능
- **Evidence:** FastAPI 공식 문서, OpenAI Python SDK

### H2: 대화 세션 관리
- 기존 `QuestionHistory` 모델에 `session_id` 컬럼 존재
- Frontend에서 `sessionStorage`로 세션 ID 관리
- **Evidence:** `backend/models/history.py`, `backend/routers/history.py:14`

### H3: UI 디자인
- ChatGPT/Claude 스타일: 중앙 컨테이너 + 메시지 버블 + 하단 입력창
- shadcn/ui 컴포넌트 활용: `Card`, `Input`, `Button`, `ScrollArea`
- **Evidence:** 기존 프로젝트는 shadcn/ui 사용 중

## Assumptions/Open Qs

### Assumptions
1. PC 화면 기준 (모바일 반응형 제외)
2. 실시간 인용 출처는 메시지 완료 후 표시
3. 토픽 변경 시 새로운 세션 생성
4. 인증은 기존 JWT 시스템 재사용

### Open Questions
- **Q1:** 스트리밍 중 에러 처리 방법?
  **A:** SSE 이벤트로 `error` 타입 전송
- **Q2:** 인용 출처는 언제 표시?
  **A:** 답변 완료 후 별도 이벤트로 전송
- **Q3:** 대화 이력 제한?
  **A:** 세션당 최근 20개 (프론트엔드 제한)

## Sub-agent Findings
N/A - 직접 구현 가능

## Risks

### R1: 스트리밍 연결 안정성
- **Mitigation:** Reconnection 로직, timeout 설정

### R2: 토큰 소비량 증가
- **Mitigation:** 대화 컨텍스트 5턴으로 제한

### R3: 동시 접속 부하
- **Mitigation:** 현 단계에서는 고려하지 않음 (향후 과제)

## Next
PLAN.md 작성 → 구현 단계별 세부 계획
