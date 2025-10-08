# Progress: Chat Slug Links

**Summary:** Chat URL을 ID 기반에서 slug 기반으로 변경

**Goal & Approach:**
Frontend routing 및 TopicSelector를 slug 기반으로 변경. Backend는 이미 `/api/topics/slug/{slug}` 제공 중이므로 변경 불필요.

## Completed Steps
- Research 완료: 관련 파일 확인, slug API 존재 확인
- Plan 작성 완료
- Step 1: Topic interface에 slug 필드 추가 (`TopicSelector.tsx:8`)
- Step 2: App.tsx routing 변경 (`/chat/:slug`)
- Step 3: TopicSelector 시그니처 변경 (`onSelectTopic(slug: string)`)
- Step 4: ChatPage slug 파라미터 처리 및 `/api/topics/slug/{slug}` 호출
- Step 5: TypeScript 및 ESLint 검사 통과 (타입 안정성 확인)
- Step 6: Backend 테스트 통과 (`test_topic_slug_routes.py` — 3 passed)
- Step 7: 커밋 완료
  - `d173f7f` [Structural] type(chat): Add slug field to Topic interface
  - `2302d1c` [Behavioral] feat(chat): Use topic slug in URLs instead of ID

## Current Failures
없음

## Next Step
태스크 완료 — TASK_SUMMARY 생성 및 아카이브
