# Plan: 청크 레벨 편집 기능

## Objective
Context 상세 페이지 내 개별 청크 편집 UI/API 구현 (content, metadata.source_page, order_index 수정 + embedding 재생성).

## Constraints
- Admin 전용 (`require_admin`)
- Celery 없이 sync 처리 (Phase 4 결정)
- OpenAI embedding 재생성 시 Qdrant 동기화 필수
- 281 테스트 기준 유지 (신규 테스트 추가)

## Target Files & Changes

### Backend
1. `backend/schemas/admin.py`
   - **Add**: `AdminContextItemUpdate` (content?: str, metadata?: dict, order_index?: int)
2. `backend/routers/admin/contexts.py`
   - **Add**: `PATCH /api/admin/contexts/{cid}/items/{iid}` endpoint
   - Logic: validate → update ContextItem → if content changed, regenerate embedding → Qdrant upsert
3. `backend/retrieval/embeddings.py`
   - **Add**: `regenerate_single_item_embedding(item: ContextItem, session: Session)` helper
4. `backend/retrieval/qdrant.py`
   - **Add**: `update_single_vector(uuid: str, vector: list[float], payload: dict)` helper

### Frontend
5. `frontend/src/pages/contexts/show.tsx`
   - **Add**: "편집" 버튼 컬럼 (각 청크 행)
   - **Add**: 편집 모달 (shadcn Dialog + Form)
   - **Add**: PATCH API 호출 로직 (React Query mutation)

### Tests
6. `backend/tests/admin/test_admin_contexts.py`
   - **Add**: `test_update_context_item_success` (content 수정)
   - **Add**: `test_update_context_item_embedding_regeneration` (embedding 재생성 확인)
   - **Add**: `test_update_context_item_metadata` (source_page 수정)
   - **Add**: `test_update_context_item_order_index` (순서 변경)
   - **Add**: `test_update_context_item_not_found` (404)
   - **Add**: `test_update_context_item_validation` (빈 content, 잘못된 metadata)

## Test/Validation Cases
- ✅ PATCH /contexts/{cid}/items/{iid} with valid content → 200 OK, content updated, new vector in Qdrant
- ✅ PATCH with metadata.source_page → metadata JSON 업데이트
- ✅ PATCH with order_index → order_index 업데이트 (unique constraint 검증)
- ✅ PATCH with empty content → 422 Unprocessable Entity
- ✅ PATCH with non-existent item_id → 404 Not Found
- ✅ PATCH with invalid metadata JSON → 422
- ✅ Frontend: 편집 버튼 클릭 → 모달 오픈 → 수정 → 저장 → 테이블 refresh

## Steps (TDD)
1. **Backend Schema** (Red→Green):
   - [ ] Write test: AdminContextItemUpdate schema validation
   - [ ] Implement: `AdminContextItemUpdate` in schemas/admin.py
2. **Backend Endpoint** (Red→Green):
   - [ ] Write test: PATCH endpoint 404 (item not found)
   - [ ] Write test: PATCH endpoint 422 (validation error)
   - [ ] Write test: PATCH endpoint 200 (content update)
   - [ ] Implement: PATCH endpoint in routers/admin/contexts.py
3. **Embedding Regeneration** (Red→Green):
   - [ ] Write test: content change → embedding regenerated
   - [ ] Implement: `regenerate_single_item_embedding` helper
   - [ ] Implement: Qdrant upsert in `update_single_vector`
4. **Frontend Edit Modal** (Manual QA):
   - [ ] Add "편집" button column in table
   - [ ] Create edit modal (Dialog + Form)
   - [ ] Wire up PATCH mutation (React Query)
   - [ ] Test: open modal → edit content → save → table refresh
5. **Integration Test**:
   - [ ] Full flow: admin login → context show → edit chunk → verify DB + Qdrant

## Rollback
- DB migration 불필요 (스키마 변경 없음)
- 코드 rollback: git revert
- Qdrant 업데이트 실패 시: DB transaction rollback

## Review Hotspots
- `regenerate_single_item_embedding`: OpenAI API 오류 처리 (retry, timeout)
- Qdrant upsert: UUID not found 시 에러 핸들링
- Frontend form validation: content 필수, metadata JSON 포맷

## Status
- [x] Step 1: Backend Schema — AdminContextItemUpdate (content: str | None, min_length=1)
- [x] Step 2: Backend Endpoint — PATCH /api/contexts/{cid}/items/{iid} (4/4 tests pass)
- [x] Step 3: Embedding Regeneration — EmbeddingService.generate_embedding() integration
- [x] Step 4: Frontend Edit Modal — show.tsx (편집 버튼 + Dialog + PATCH call + refresh)
- [x] Step 5: Quality Verification — 100 tests pass, mypy pass, frontend build success
