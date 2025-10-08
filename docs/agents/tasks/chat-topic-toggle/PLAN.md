# Plan: Chat Topic Toggle

**Objective:** 토픽 선택 시 사이드바를 토글로 숨기고 표시할 수 있는 기능 추가

**Constraints:**
- 토픽 미선택 시에는 사이드바 항상 표시 (숨김 불가)
- 반응형 레이아웃 유지
- 토글 상태는 localStorage에 저장하여 다음 방문 시 유지

## Target Files & Changes

### Frontend
1. **`frontend/src/pages/chat/index.tsx`**
   - `isSidebarVisible` state 추가 (초기값: localStorage 또는 true)
   - 토글 버튼 UI 추가 (헤더 또는 메인 영역 좌상단)
   - `<aside>` 조건부 렌더링 또는 CSS 클래스 전환
   - localStorage에 토글 상태 저장
   - 토픽 미선택 시 사이드바 강제 표시

## Test/Validation Cases

### Manual Test
1. 토픽 미선택 상태: 토글 버튼 비활성화 또는 숨김, 사이드바 항상 표시
2. 토픽 선택 상태: 토글 버튼 활성화, 클릭 시 사이드바 숨김/표시
3. 사이드바 숨김 상태에서 메인 영역 전체 너비 확장 확인
4. 페이지 새로고침 시 토글 상태 유지 (localStorage)
5. 반응형: 작은 화면에서 레이아웃 정상 작동

## Steps

1. **[Structural]** ChatPage에 `isSidebarVisible` state 및 localStorage 연동 추가
2. **[Behavioral]** 토글 버튼 UI 추가 (Lucide icon 사용)
3. **[Behavioral]** 사이드바 조건부 렌더링 및 CSS transition
4. **[Behavioral]** 토픽 미선택 시 사이드바 강제 표시 로직
5. **[Refactor]** CSS 정리, 애니메이션 최적화
6. **[Validation]** 수동 테스트 (브라우저, 반응형)
7. **[Commit]** `[Behavioral] feat(chat): Add sidebar toggle for topic selector [chat-topic-toggle]`

## Rollback
- Git revert로 즉시 복원 가능
- UI 변경만 있으므로 데이터 영향 없음

## Review Hotspots
- `ChatPage.tsx`: 토글 버튼 위치 및 UX
- CSS transition 성능
- localStorage 키 네이밍 일관성

## Status
- [x] Step 1: State 및 localStorage 연동
- [x] Step 2: 토글 버튼 UI
- [x] Step 3: 사이드바 조건부 렌더링
- [x] Step 4: 토픽 미선택 시 강제 표시 (Step 3에 통합)
- [x] Step 5: Refactor (TypeScript/ESLint 통과)
- [x] Step 6: Manual validation
- [ ] Step 7: Commit
