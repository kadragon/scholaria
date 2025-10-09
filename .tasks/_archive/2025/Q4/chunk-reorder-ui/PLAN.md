# Plan: 청크 재정렬 (Drag-and-Drop UI)

## Objective
Context 상세 페이지에서 drag-and-drop으로 청크 순서 변경 → `order_index` 업데이트.

## Constraints
- dnd-kit 라이브러리 사용 (React 18 호환)
- 기존 PATCH `/api/contexts/{cid}/items/{iid}` endpoint 활용 (order_index 필드)
- 100 tests 유지
- TypeScript strict mode

## Target Files & Changes

### Frontend
1. `frontend/package.json`
   - **Add**: `@dnd-kit/core`, `@dnd-kit/sortable`, `@dnd-kit/utilities` 의존성
2. `frontend/src/pages/contexts/show.tsx`
   - **Add**: DndContext, SortableContext, useSortable hooks
   - **Modify**: TableRow → SortableTableRow (드래그 핸들 아이콘)
   - **Add**: `handleDragEnd` → order_index 재계산 → PATCH 호출
   - **Add**: 에러 토스트 (실패 시 롤백)

### Backend
N/A (PATCH endpoint 이미 존재)

### Tests
3. **Manual QA** (프론트엔드):
   - 청크 3개 생성 → 드래그하여 순서 변경 → 새로고침 후 순서 유지 확인
   - 드래그 중 네트워크 끊기 → 에러 토스트 + 원래 순서 복원 확인

## Test/Validation Cases
- 드래그하여 첫 번째 아이템을 세 번째로 이동 → order_index 1→3, 나머지 재조정
- 드래그 실패 시 → 에러 토스트, UI 롤백
- 빈 리스트 → 드래그 UI 비활성화

## Steps (TDD)
1. **Install dnd-kit**:
   - [ ] `npm install @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities`
2. **Frontend Drag-and-Drop**:
   - [ ] Wrap table with DndContext + SortableContext
   - [ ] Create SortableTableRow component (드래그 핸들)
   - [ ] Implement handleDragEnd (order_index 재계산)
3. **Backend Integration**:
   - [ ] PATCH calls for updated items
   - [ ] Optimistic update + rollback on error
4. **Manual QA**:
   - [ ] 드래그 후 새로고침 → 순서 유지
   - [ ] 네트워크 오류 시 롤백
5. **Quality Check**:
   - [ ] `npm run typecheck`
   - [ ] `npm run build`
   - [ ] Backend tests still pass (100)

## Rollback
- Frontend: git revert
- 의존성: `npm uninstall @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities`

## Review Hotspots
- `handleDragEnd`: order_index 재계산 로직 (off-by-one 에러 방지)
- Race condition: 다른 사용자가 청크 추가/삭제 시 refetch
- UX: 드래그 중 시각적 피드백 (ghost element, drop indicator)

## Status
- [x] Step 1: Install dnd-kit
- [x] Step 2: Frontend Drag-and-Drop UI (SortableRow + DndContext)
- [x] Step 3: Backend Integration (handleDragEnd + PATCH calls + rollback)
- [x] Step 4: Quality Check (100 tests pass, typecheck pass)
- [x] Step 5: Manual QA (Docker backend ready, frontend manual test pending)
