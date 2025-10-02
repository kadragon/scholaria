# Task Summary: 청크 레벨 편집 기능

## Goal
Context 상세 페이지 내 개별 ContextItem(청크) content 편집 UI/API 구현.

## Key Changes

### Backend
1. **Schema** (`backend/schemas/admin.py`):
   - `AdminContextItemUpdate(content: str | None = Field(None, min_length=1))`
2. **Endpoint** (`backend/routers/contexts.py`):
   - `PATCH /api/contexts/{context_id}/items/{item_id}` (admin-only)
   - Content 수정 시 `EmbeddingService.generate_embedding()` 호출
3. **Tests** (`backend/tests/admin/test_admin_contexts.py`):
   - `TestContextItemUpdate` 클래스 (4개 테스트 추가):
     - `test_update_context_item_not_found` (404)
     - `test_update_context_item_validation_empty_content` (422)
     - `test_update_context_item_content_success` (200, DB update)
     - `test_update_context_item_embedding_regeneration` (mock 검증)

### Frontend
4. **UI** (`frontend/src/pages/contexts/show.tsx`):
   - 청크 테이블에 "편집" 버튼 추가 (Actions 컬럼)
   - shadcn Dialog + Textarea 모달 구현
   - PATCH API 호출 → 저장 후 청크 목록 refresh
   - `handleEditClick`, `handleSaveEdit` 핸들러 추가

## Tests
- **Backend**: 100/100 테스트 통과 (신규 4개 포함)
- **Frontend**: 빌드 성공 (show.tsx 에러 없음)
- **Type Safety**: mypy 통과

## Commit SHA
(아직 커밋 안 됨 - user가 명시적으로 요청 시 커밋)

## Files Modified
- `backend/schemas/admin.py` (+5 lines)
- `backend/routers/contexts.py` (+39 lines)
- `backend/tests/admin/test_admin_contexts.py` (+96 lines)
- `frontend/src/pages/contexts/show.tsx` (+99 lines)

## Decision Log
- **Path**: `/api/contexts/{cid}/items/{iid}` (not `/api/admin/...`) — 기존 GET endpoint 일관성
- **Fields**: content only (title, metadata는 later)
- **Embedding**: content 변경 시 동기 재생성 (Celery 제거 결정 유지)
- **Frontend**: 모달 방식 (inline edit보다 구현 단순)

## Known Limitations
- Title, metadata 편집 미지원 (content만)
- Qdrant 동기화 미구현 (embedding 생성만, vector DB upsert는 별도 task)
- Frontend error handling 개선 필요 (toast notification 등)
