# Research: Frontend Phase 2 – Component Interaction Tests

## Goal
공용 컴포넌트의 사용자 상호작용, 키보드 동작, 접근성 검증 테스트 작성

## Scope
- `InlineEditCell`: 더블클릭 편집, Enter/Escape 키, blur 시 저장
- `CommandPalette`: 명령 검색, 네비게이션, 키보드 선택
- `TableSkeleton`: rows/columns props에 따른 렌더링
- `ui/checkbox`: 체크/언체크, 키보드 포커스
- `ui/collapsible`: 토글 동작
- `ui/tabs`: 탭 전환, 키보드 내비게이션
- `use-toast`: toast 추가/삭제/업데이트, TOAST_LIMIT 검증

## Related Files
- `/Users/kadragon/Dev/scholaria/frontend/src/components/InlineEditCell.tsx` — 인라인 편집 셀 (70줄)
- `/Users/kadragon/Dev/scholaria/frontend/src/components/CommandPalette.tsx` — 명령 팔레트 (80줄)
- `/Users/kadragon/Dev/scholaria/frontend/src/components/TableSkeleton.tsx` — 테이블 스켈레톤 (45줄)
- `/Users/kadragon/Dev/scholaria/frontend/src/hooks/use-toast.ts` — 토스트 훅 (190줄)
- `/Users/kadragon/Dev/scholaria/frontend/src/components/ui/checkbox.tsx` — Radix Checkbox 래퍼
- `/Users/kadragon/Dev/scholaria/frontend/src/components/ui/collapsible.tsx` — Radix Collapsible 래퍼
- `/Users/kadragon/Dev/scholaria/frontend/src/components/ui/tabs.tsx` — Radix Tabs 래퍼

## Evidence & Patterns

### InlineEditCell
- **더블클릭** → isEditing true → input 포커스 & select
- **Enter** → handleSave (trim, 변경 확인, onSave 호출)
- **Escape** → handleCancel (원래 값 복원)
- **Blur** → handleSave
- **테스트 케이스**:
  1. 더블클릭 시 input 모드 진입
  2. Enter 키로 저장 & onSave 호출
  3. Escape 키로 취소 & 원래 값 복원
  4. blur 시 저장
  5. 빈 값/공백만 있는 값 저장 무시
  6. 변경 없으면 onSave 미호출

### CommandPalette
- **open prop** 제어로 CommandDialog 표시
- **CommandItem onSelect** → runCommand → onOpenChange(false) + navigate
- **React Router navigate** 모킹 필요
- **테스트 케이스**:
  1. open=true 시 다이얼로그 렌더링
  2. 명령 선택 시 navigate 호출
  3. 명령 선택 후 onOpenChange(false) 호출
  4. 검색어 없을 때 "검색 결과가 없습니다" 표시

### TableSkeleton
- **rows, columns props**로 Skeleton 그리드 생성
- 기본값: rows=8, columns=5
- **테스트 케이스**:
  1. 기본 props로 8x5 Skeleton 렌더링
  2. 커스텀 rows/columns props 반영
  3. TableHeader/TableBody 존재 확인

### use-toast
- **toast()** 호출 → ADD_TOAST dispatch
- **TOAST_LIMIT = 1** → 최대 1개 토스트만 유지
- **dismiss(id)** → DISMISS_TOAST → addToRemoveQueue
- **테스트 케이스**:
  1. toast() 호출 시 toasts 배열에 추가
  2. TOAST_LIMIT 초과 시 오래된 토스트 제거
  3. dismiss 호출 시 open=false로 변경
  4. 여러 컴포넌트에서 useToast 호출 시 동일 상태 공유

### ui/checkbox, ui/collapsible, ui/tabs
- **Radix UI primitives** 래퍼 → Radix 자체 테스트 커버리지 높음
- 커스텀 스타일/동작 없음 → **우선순위 낮음**, shadcn/ui 컴포넌트는 통합 테스트에서 간접 검증
- **테스트 전략**: 통합 테스트(페이지 시나리오)에서 검증 예정

## Assumptions
- React Router useNavigate는 vi.fn()으로 모킹
- @testing-library/user-event 사용 (키보드 이벤트, 더블클릭)
- Radix UI primitives는 별도 단위 테스트 불필요(shadcn/ui 래퍼)

## Risks
- InlineEditCell input focus/select는 jsdom 환경에서 제한적
- CommandPalette는 Radix CommandDialog 의존 → 복잡한 키보드 내비게이션 모킹 필요
- use-toast의 setTimeout 기반 로직 → vi.useFakeTimers 필요

## Next
PLAN 작성 → 우선순위: InlineEditCell > TableSkeleton > use-toast > CommandPalette
