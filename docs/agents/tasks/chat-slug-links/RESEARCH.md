# Research: Chat Slug Links

**Goal:** Chat 화면의 URL을 ID 기반에서 slug 기반으로 변경하여 더 읽기 쉽고 의미 있는 링크 제공

**Scope:** Frontend routing 및 API client 모듈

## Related Files
- `frontend/src/pages/chat/*` — 채팅 라우팅 및 컴포넌트
- `frontend/src/lib/apiClient.ts` — API 호출 레이어
- `frontend/src/App.tsx` — 라우트 정의
- `backend/routers/topics.py` — topic slug 엔드포인트 제공 여부
- `backend/routers/history.py` — 히스토리 조회 엔드포인트

## Hypotheses
1. 현재 chat URL은 `/chat/:topicId` 형태로 ID를 사용
2. Backend에 이미 slug 기반 topic 조회 엔드포인트 존재 가능성 높음 (과거 작업 참조)
3. Frontend routing만 변경하고 API client에서 slug→ID 변환 필요할 수 있음
4. 히스토리 세션 ID는 유지되어야 하므로 topic slug만 변경 대상

## Evidence
1. **Frontend routing**: `App.tsx:50` — `/chat/:topicId` 경로 사용 (ID 기반)
2. **Backend API**: `backend/routers/topics.py:25-35` — `/api/topics/slug/{slug}` 엔드포인트 **이미 존재**
3. **ChatPage**: `frontend/src/pages/chat/index.tsx:13` — `topicId` 파라미터를 parseInt로 처리
4. **TopicSelector**: `frontend/src/pages/chat/components/TopicSelector.tsx:58` — `topic.id` 기준으로 선택/navigate
5. **Topic schema**: Backend의 `TopicOut`은 `id`, `name`, `description`, `slug` 모두 포함 (추정)

## Assumptions
- Backend `/api/topics/by-slug/{slug}` 엔드포인트 존재 (확인 필요)
- Frontend에서 slug를 URL에 사용하고 내부적으로 ID 매핑
- 기존 북마크/링크 호환성은 고려하지 않음 (신규 설계)

## Open Questions
- Session ID는 URL에 계속 포함되는가? (`/chat/:topicSlug/:sessionId`)
- 새 채팅 시작 시 slug만으로 라우팅 가능한가?

## Risks
- Topic slug 중복 가능성 (DB 제약 확인 필요)
- 기존 북마크 링크 깨짐 (신규 설계이므로 무시)

## Next
1. Backend `TopicOut` schema에 slug 필드 확인
2. Plan 작성: Frontend routing 변경, TopicSelector 수정, ChatPage 파라미터 처리
3. TDD 흐름: slug 기반 topic 조회 테스트 → routing 변경 → integration test
