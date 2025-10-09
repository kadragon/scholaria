# Plan: Frontend Phase 2 – Component Interaction Tests

## Objective
공용 컴포넌트의 사용자 상호작용 로직 검증 테스트 작성

## Constraints
- @testing-library/user-event 사용 권장
- Radix UI primitives 래퍼(checkbox/collapsible/tabs)는 통합 테스트에서 검증 → 별도 단위 테스트 생략
- 키보드 이벤트, 포커스, 접근성 동작 포함

## Target Files & Changes

### New Test Files
1. `frontend/src/components/__tests__/InlineEditCell.test.tsx`
   - 더블클릭 → 편집 모드
   - Enter → 저장
   - Escape → 취소
   - blur → 저장
   - 빈 값/변경 없음 처리

2. `frontend/src/components/__tests__/TableSkeleton.test.tsx`
   - 기본 props (8x5)
   - 커스텀 rows/columns
   - TableHeader/TableBody 렌더링

3. `frontend/src/hooks/__tests__/use-toast.test.ts`
   - toast() 호출
   - TOAST_LIMIT 검증
   - dismiss()
   - 여러 컴포넌트 간 상태 공유

4. `frontend/src/components/__tests__/CommandPalette.test.tsx`
   - open prop 제어
   - 명령 선택 & navigate
   - onOpenChange 호출

## Steps

1. **[Structural] InlineEditCell 테스트 작성**
   - user-event로 dblClick, keyboard, blur 시뮬레이션
   - onSave 모킹 & 호출 검증
   - TDD: Red → Green → Refactor

2. **[Structural] TableSkeleton 테스트 작성**
   - props별 Skeleton 개수 검증
   - TDD: Red → Green → Refactor

3. **[Structural] use-toast 테스트 작성**
   - vi.useFakeTimers 사용
   - renderHook으로 상태 검증
   - TDD: Red → Green → Refactor

4. **[Structural] CommandPalette 테스트 작성**
   - useNavigate 모킹
   - user-event로 명령 선택
   - TDD: Red → Green → Refactor

5. **[Behavioral] 전체 테스트 실행 & 검증**
   - npm test 통과 확인
   - lint/typecheck 통과

## Validation
- 모든 신규 테스트 통과
- 기존 테스트 regression 없음
- `npm run lint`, `npm run typecheck` 통과

## Rollback
- 각 커밋은 독립적으로 revert 가능
- 테스트 파일만 추가되므로 기능 코드 영향 없음

## Review Hotspots
- InlineEditCell의 focus/select 동작 (jsdom 제약)
- use-toast의 setTimeout 기반 로직
- CommandPalette의 Radix Command 모킹

## Status
- [ ] Step 1: InlineEditCell 테스트 작성 (TDD)
- [ ] Step 2: TableSkeleton 테스트 작성 (TDD)
- [ ] Step 3: use-toast 테스트 작성 (TDD)
- [ ] Step 4: CommandPalette 테스트 작성 (TDD)
- [ ] Step 5: 전체 테스트 실행 & 검증
