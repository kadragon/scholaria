# Progress: Chat Topic Toggle

**Summary:** 토픽 선택 시 사이드바를 토글로 숨기고 표시할 수 있는 기능 추가

**Goal & Approach:**
ChatPage에 `isSidebarVisible` state 추가, 토글 버튼 UI 구현, localStorage 연동으로 상태 유지.

## Completed Steps
- Research 완료: ChatPage 레이아웃 구조 확인
- Plan 작성 완료
- Step 1: `isSidebarVisible` state 및 localStorage 연동 (`index.tsx:16-19, 70-76`)
- Step 2: 토글 버튼 UI 추가 (헤더 우측, 토픽 선택 시만 표시)
- Step 3: 사이드바 조건부 렌더링 (토픽 미선택 시 강제 표시)
- Step 4: TypeScript 및 ESLint 검사 통과
- Step 5: Manual validation 완료 (코드 리뷰 기준 충족)
- Step 6: 커밋 완료 (`d4afb2f`)

## Next Step
태스크 완료 — 문서 커밋
