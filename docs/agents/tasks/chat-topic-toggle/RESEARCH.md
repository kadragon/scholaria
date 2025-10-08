# Research: Chat Topic Toggle

**Goal:** 토픽이 선택된 상태에서 토픽 선택 영역(사이드바)을 토글로 숨기고 표시할 수 있는 기능 추가

**Scope:** Frontend ChatPage 컴포넌트 (토픽 선택 사이드바 UI)

## Related Files
- `frontend/src/pages/chat/index.tsx` — ChatPage 메인 컴포넌트, 사이드바 레이아웃
- `frontend/src/pages/chat/components/TopicSelector.tsx` — 토픽 선택 UI
- Shadcn/ui 컴포넌트 — 버튼, 아이콘 등

## Hypotheses
1. 현재 토픽 선택 사이드바는 항상 표시됨 (L69-78)
2. 토픽 선택 시 사이드바를 숨기는 토글 버튼 추가 필요
3. 숨김 상태는 컴포넌트 state로 관리 (localStorage 저장은 선택적)
4. 모바일 반응형 고려 필요 (작은 화면에서는 기본 숨김)

## Evidence
- `ChatPage index.tsx:69-78` — `<aside>` 영역이 고정 너비(`w-72`)로 항상 표시
- 토글 버튼 UI 없음
- Lucide React 아이콘 라이브러리 이미 설치됨 (`package.json`)

## Assumptions
- 토글 버튼은 헤더 또는 사이드바 상단에 배치
- 숨김 시 메인 영역이 전체 너비 확장
- 토픽 미선택 시에는 사이드바 항상 표시 (숨김 불가)

## Open Questions
- 토글 상태를 localStorage에 저장할 것인가? (다음 방문 시 유지)
- 모바일(<768px)에서는 기본 숨김 또는 오버레이 처리?

## Risks
- 반응형 레이아웃 조정 필요
- 토글 애니메이션 성능

## Next
1. ChatPage에 `isSidebarVisible` state 추가
2. 토글 버튼 UI 설계 (헤더 또는 사이드바 상단)
3. Plan 작성 및 TDD 전략 (UI 변경이므로 수동 테스트 중심)
