# Plan: Chat Slug Links

**Objective:** Chat 화면의 URL을 `/chat/:topicId` → `/chat/:slug` 로 변경하여 더 읽기 쉬운 링크 제공

**Constraints:**
- Backend slug API (`/api/topics/slug/{slug}`) 이미 존재
- 기존 테스트 깨지지 않게 유지
- Session ID는 URL에 포함하지 않음 (sessionStorage 유지)

## Target Files & Changes

### Frontend
1. **`frontend/src/App.tsx`**
   - L50: `/chat/:topicId` → `/chat/:slug`

2. **`frontend/src/pages/chat/index.tsx`**
   - L13: `topicId` → `slug` 파라미터로 변경
   - L31-41: slug로 topic 조회 후 `selectedTopicId` 설정
   - L59: `navigate(/chat/${topicId})` → `navigate(/chat/${slug})`
   - `selectedTopicId` state는 내부적으로 유지 (API 호출용)

3. **`frontend/src/pages/chat/components/TopicSelector.tsx`**
   - L8: `onSelectTopic` 시그니처 변경: `(topicId: number) → (slug: string)`
   - L58: `onSelectTopic(topic.id)` → `onSelectTopic(topic.slug)`
   - Interface에 `slug: string` 추가

4. **`frontend/src/lib/apiClient.ts`** (변경 불필요 — slug 조회는 fetch 직접 사용)

### Backend
- 변경 없음 (`/api/topics/slug/{slug}` 엔드포인트 이미 존재)

## Test/Validation Cases

### Backend Integration Test (기존 유지)
- `backend/tests/test_topic_slug_routes.py` — slug 엔드포인트 정상 작동 확인

### Manual Test
- 브라우저에서 `/chat/python-programming` 같은 slug URL 직접 접근
- Topic 선택 시 URL이 slug로 변경되는지 확인
- 잘못된 slug 접근 시 에러 처리 확인

## Steps

1. **[Structural]** TypeScript 타입 정의 정리 (Topic interface에 slug 추가)
2. **[Behavioral]** `App.tsx` routing 변경 (`/chat/:topicId` → `/chat/:slug`)
3. **[Behavioral]** `TopicSelector` 변경 (slug 전달 및 interface 업데이트)
4. **[Behavioral]** `ChatPage` slug 파라미터 처리 및 API 호출
5. **[Refactor]** 에러 핸들링 및 타입 안정성 보강
6. **[Validation]** 수동 테스트 — 브라우저 확인 및 기존 backend 테스트 재실행
7. **[Commit]** `[Behavioral] feat(chat): Use topic slug in URLs instead of ID [chat-slug-links]`

## Rollback
- Git revert 또는 브랜치 전환으로 즉시 복원 가능
- Backend API 변경 없으므로 안전

## Review Hotspots
- `ChatPage.tsx` L31-41: slug→ID 매핑 로직 (API 에러 핸들링)
- `TopicSelector.tsx`: Interface 변경 및 하위 컴포넌트 영향도
- 테스트 커버리지: slug 기반 routing 시나리오

## Status
- [x] Step 1: TypeScript 타입 정의
- [x] Step 2: App.tsx routing 변경
- [x] Step 3: TopicSelector 변경
- [x] Step 4: ChatPage slug 처리
- [x] Step 5: Refactor
- [x] Step 6: Manual validation
- [x] Step 7: Commit Commit
