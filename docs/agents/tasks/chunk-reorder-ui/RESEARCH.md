# Research: 청크 재정렬 (Drag-and-Drop UI)

## Goal
Context 상세 페이지에서 청크를 drag-and-drop으로 재정렬하여 `order_index` 업데이트.

## Scope
- Frontend: `show.tsx`에 drag-and-drop 기능 추가
- Backend: PATCH endpoint로 order_index 업데이트 (이미 존재하는 `/api/contexts/{cid}/items/{iid}` 활용)

## Related Files/Flows
- `frontend/src/pages/contexts/show.tsx`: 청크 목록 테이블 (편집 기능 이미 구현)
- `backend/routers/admin/contexts.py`: PATCH endpoint 이미 존재 (`order_index` 필드 지원)
- `backend/schemas/admin.py`: `AdminContextItemUpdate` (order_index 포함)

## Hypotheses
1. **dnd-kit 사용**: React 생태계에서 가장 널리 사용되는 drag-and-drop 라이브러리
2. **Optimistic update**: 드래그 후 즉시 UI 업데이트, 백엔드 실패 시 롤백
3. **Batch update**: 여러 아이템의 order_index를 한 번에 업데이트하는 것이 효율적

## Evidence
- `package.json`: dnd-kit 미설치 확인 → 설치 필요
- `show.tsx`: 이미 편집 기능 존재 (`handleEditClick`, `handleSaveEdit`)
- PATCH endpoint는 `content`, `metadata`, `order_index` 모두 optional

## Assumptions/Open Qs
- **Q**: Batch update API가 필요한가?
  - **A**: 초기에는 개별 PATCH로 구현, 성능 이슈 발생 시 batch endpoint 추가
- **Q**: 드래그 중 다른 사용자가 청크를 추가/삭제하면?
  - **A**: 재정렬 후 refetch하여 최신 상태 동기화 (낙관적 업데이트로 UX 유지)
- **Q**: `order_index`가 중복되면?
  - **A**: 백엔드에서 unique constraint 없으므로 허용, 프론트엔드에서 재계산하여 1, 2, 3... 순서 보장

## Sub-agent Findings
N/A

## Risks
1. **Race condition**: 동시 편집 시 order_index 충돌 → refetch로 해결
2. **UX**: 드래그 중 네트워크 오류 → 에러 토스트 + 롤백
3. **Performance**: 많은 청크(100+) 드래그 시 느려질 수 있음 → 가상화 고려 (향후)

## Next
Plan 작성 → TDD 구현
