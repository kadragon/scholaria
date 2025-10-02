# Progress: 청크 레벨 편집 기능

## Summary
Context 상세 페이지 내 청크 편집 UI/API 구현 진행 중 (Step 2/5 완료).

## Goal & Approach
- **Goal**: ContextItem content 수정 → embedding 재생성 → Qdrant 동기화
- **Approach**: TDD (Red→Green→Refactor) + Stepwise Implementation

## Completed Steps
1. ✅ **Backend Schema** (AdminContextItemUpdate):
   - `content: str | None = Field(None, min_length=1)`
   - Validation: empty content → 422
2. ✅ **Backend Endpoint** (PATCH /api/contexts/{cid}/items/{iid}):
   - 4/4 tests passing:
     - `test_update_context_item_not_found` (404)
     - `test_update_context_item_validation_empty_content` (422)
     - `test_update_context_item_content_success` (200, DB update verified)
     - `test_update_context_item_embedding_regeneration` (embedding service called)
   - Admin-only dependency (`require_admin`)
   - Content update + embedding regeneration
3. ✅ **Embedding Regeneration**:
   - `EmbeddingService.generate_embedding()` 호출 (content 변경 시)
   - Mock 테스트로 OpenAI API 호출 검증
   - 100/100 전체 테스트 통과
4. ✅ **Frontend Edit Modal** (`frontend/src/pages/contexts/show.tsx`):
   - 청크 테이블에 "편집" 버튼 추가 (Actions 컬럼)
   - shadcn Dialog + Textarea + Label 사용
   - PATCH /api/contexts/{cid}/items/{iid} 호출 (fetch)
   - 저장 후 청크 목록 refresh
   - Frontend 빌드 성공 (no errors)

## Current Failures
None.

## Decision Log
- **Path**: `/api/contexts/{cid}/items/{iid}` (not `/api/admin/...`) — 기존 GET endpoint와 일관성 유지.
- **Fields**: content only for now (title, metadata 추가는 later).
- **ContextItem model fields**: title (str), content (str), item_metadata (JSON), file_path (str | None) — no `order_index` or `vector` in DB schema.

## Completed
✅ 모든 단계 완료 (Step 1-5).
- Backend: PATCH endpoint + embedding regeneration + 4 tests
- Frontend: 편집 모달 + API 호출
- Quality: 100/100 테스트 통과, mypy 통과, frontend 빌드 성공

## Next
User가 커밋 요청 시 커밋 생성.
