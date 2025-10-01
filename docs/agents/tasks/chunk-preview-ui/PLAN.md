# Plan: Chunk Preview UI Enhancement

## Objective

Context 상세 페이지에서 ContextItem(청크) 목록을 미리보기와 함께 표시하여 관리자가 콘텐츠 처리 상태를 확인할 수 있도록 개선

## Constraints

- TDD 필수 (backend API)
- 기존 API 호환성 유지 (새 엔드포인트 추가)
- Refine 패턴 준수 (frontend)
- 성능 고려 (페이지네이션 또는 제한)

## Target Files & Changes

### Backend

1. **`backend/routers/contexts.py`** (신규 엔드포인트):
   - `GET /contexts/{context_id}/items` 추가
   - Response: `list[ContextItemOut]`
   - Query params: `skip=0`, `limit=100` (기본값)

2. **`backend/tests/test_contexts.py`** (기존 테스트 확장):
   - `test_get_context_items_success` (정상 조회)
   - `test_get_context_items_empty` (청크 없는 경우)
   - `test_get_context_items_not_found` (Context 없음)
   - `test_get_context_items_pagination` (limit/offset)

### Frontend

3. **`frontend/src/pages/contexts/show.tsx`** (신규):
   - Context 메타데이터 표시 (name, description, type, chunk_count, status)
   - ContextItem 목록 표시 (Table 또는 Card)
   - "Edit" / "Back to List" 버튼

4. **`frontend/src/pages/contexts/list.tsx`** (수정):
   - "Edit" 버튼 옆에 "View" 버튼 추가
   - `show("contexts", context.id)` 호출

5. **`frontend/src/App.tsx`** (라우팅 추가):
   - `/admin/contexts/:id` 경로 추가

## Test/Validation Cases

### Backend (TDD)
1. ✅ 청크가 있는 Context 조회 → 200 + list[ContextItemOut]
2. ✅ 청크가 없는 Context 조회 → 200 + []
3. ✅ 존재하지 않는 Context → 404
4. ✅ 페이지네이션 (skip=0, limit=2) → 2개 반환
5. ✅ Datetime 직렬화 (ISO format)

### Frontend (Manual)
1. Context list에서 "View" 클릭 → 상세 페이지 이동
2. 상세 페이지에서 청크 목록 표시 확인
3. 청크가 없는 경우 "No chunks" 메시지
4. "Edit" 버튼 → 편집 페이지 이동
5. "Back" 버튼 → 목록 페이지 복귀

## Steps

### Phase 1: Backend API (TDD)
1. [ ] 테스트 작성: `test_get_context_items_not_found` (Red)
2. [ ] 구현: `GET /contexts/{id}/items` 엔드포인트 (Green)
3. [ ] 테스트 작성: `test_get_context_items_empty` (Red)
4. [ ] 구현: 빈 목록 반환 로직 (Green)
5. [ ] 테스트 작성: `test_get_context_items_success` (Red)
6. [ ] 구현: ContextItem 쿼리 및 반환 (Green)
7. [ ] 테스트 작성: `test_get_context_items_pagination` (Red)
8. [ ] 구현: skip/limit 파라미터 (Green)
9. [ ] Refactor: 중복 제거, 코드 정리

### Phase 2: Frontend UI
10. [ ] 라우팅 추가: `App.tsx`에 `/admin/contexts/:id` 경로
11. [ ] 페이지 생성: `show.tsx` (기본 레이아웃)
12. [ ] API 연동: `useOne` + custom hook for items
13. [ ] 청크 목록 UI: Table 컴포넌트 (title, content preview, created_at)
14. [ ] List 페이지 수정: "View" 버튼 추가

### Phase 3: Integration & Polish
15. [ ] E2E 테스트: List → Show → Edit 플로우
16. [ ] 성능 검증: 100개 이상 청크 로드 테스트
17. [ ] UI 개선: 로딩 상태, 에러 핸들링
18. [ ] 문서 업데이트: PROGRESS.md, AGENTS.md

## Rollback

- Backend: 새 엔드포인트 제거 (`git revert` 가능)
- Frontend: 라우팅 및 컴포넌트 제거 (`git revert` 가능)
- 기존 기능 영향 없음 (새 기능 추가만)

## Review Hotspots

1. **Backend**:
   - Pagination 로직 (off-by-one 에러 주의)
   - Datetime serialization (`@field_serializer` 적용 확인)
   - N+1 쿼리 방지 (현재는 단순 join 없으므로 문제 없음)

2. **Frontend**:
   - 라우팅 충돌 (`/admin/contexts/:id` vs `/admin/contexts/create`)
   - Content preview 길이 제한 (긴 텍스트 truncate)
   - 빈 상태 처리 (청크 0개)

## Status

- [ ] Step 1: Backend test (404 case)
- [ ] Step 2: Backend implementation (basic endpoint)
- [ ] Step 3: Backend test (empty list)
- [ ] Step 4: Backend implementation (empty list)
- [ ] Step 5: Backend test (success case)
- [ ] Step 6: Backend implementation (items query)
- [ ] Step 7: Backend test (pagination)
- [ ] Step 8: Backend implementation (skip/limit)
- [ ] Step 9: Refactor backend
- [ ] Step 10: Frontend routing
- [ ] Step 11: Frontend show page
- [ ] Step 12: Frontend API integration
- [ ] Step 13: Frontend chunk list UI
- [ ] Step 14: Frontend list update
- [ ] Step 15: E2E testing
- [ ] Step 16: Performance validation
- [ ] Step 17: UI polish
- [ ] Step 18: Documentation
