# Task Summary: 청크 재정렬 (Drag-and-Drop UI)

## Goal
Context 상세 페이지에서 drag-and-drop으로 청크 순서 변경

## Key Changes
1. **Dependencies**: `@dnd-kit/core`, `@dnd-kit/sortable`, `@dnd-kit/utilities` 설치
2. **Frontend** (`show.tsx`):
   - DndContext, SortableContext 추가
   - SortableRow 컴포넌트 (GripVertical 드래그 핸들)
   - handleDragEnd: arrayMove → order_index 재계산 → PATCH 호출
   - 에러 처리: 실패 시 이전 상태 롤백 + 토스트
3. **Backend**: 기존 PATCH endpoint 활용 (`/api/contexts/{cid}/items/{iid}`)

## Tests
- ✅ Backend: 100 tests pass (청크 업데이트 4개 포함)
- ✅ TypeScript typecheck pass
- ⏸️ Manual QA pending (Docker 환경)

## Files Modified
- `frontend/package.json`
- `frontend/src/pages/contexts/show.tsx`

## Commits
N/A (manual QA 후 커밋)

## Notes
- Optimistic update: 드래그 즉시 UI 반영, 네트워크 오류 시 롤백
- Batch update API 미구현 (향후 성능 이슈 시 추가 고려)
