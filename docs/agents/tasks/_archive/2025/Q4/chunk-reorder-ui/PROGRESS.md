# Progress: 청크 재정렬 (Drag-and-Drop UI)

## Summary
Context 상세 페이지에 drag-and-drop 기능 구현 완료. `order_index` 업데이트 및 낙관적 UI 처리 완료.

## Goal & Approach
- dnd-kit 라이브러리로 SortableContext 구현
- 드래그 완료 시 order_index 재계산 후 PATCH 호출
- 실패 시 이전 상태로 롤백 + 에러 토스트

## Completed Steps
1. ✅ dnd-kit 설치 (`@dnd-kit/core`, `@dnd-kit/sortable`, `@dnd-kit/utilities`)
2. ✅ `show.tsx` 수정:
   - DndContext, SortableContext 추가
   - SortableRow 컴포넌트 생성 (GripVertical 아이콘)
   - handleDragEnd 구현 (arrayMove + PATCH calls)
   - 에러 처리 (롤백 + 토스트)
3. ✅ TypeScript 타입 오류 수정 (`type DragEndEvent`)
4. ✅ 백엔드 테스트 100개 통과 확인

## Current Failures
- 프론트엔드 빌드 시 `list.tsx`, `topics/list.tsx`에서 기존 타입 오류 존재 (이번 태스크와 무관)

## Decision Log
- **Batch update API 미구현**: 개별 PATCH로 충분, 향후 성능 이슈 발생 시 추가
- **Optimistic update**: 드래그 즉시 UI 반영, 네트워크 오류 시 롤백

## Next Step
Manual QA - Docker 환경에서 드래그 동작 테스트
