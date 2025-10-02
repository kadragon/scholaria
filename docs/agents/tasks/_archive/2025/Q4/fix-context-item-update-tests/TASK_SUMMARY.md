# Task Summary: Fix Context Item Update Tests

## Goal
3개 실패 테스트 수정 (134 tests now passing)

## Key Changes
- **File:** `backend/tests/admin/test_admin_contexts.py` (line 238, 275, 321)
- **Change:** Mock target `backend.routers.contexts.EmbeddingService` → `backend.tasks.embeddings.regenerate_embedding_task`
- **Reason:** 실제 구현은 Celery task를 호출하지만, 테스트는 존재하지 않는 EmbeddingService를 모킹하려 함

## Tests
- ✅ `test_update_context_item_validation_empty_content`
- ✅ `test_update_context_item_content_success`
- ✅ `test_update_context_item_embedding_regeneration`
- ✅ All 134 tests passing

## Commit
- SHA: 76cf3c5
- Message: `[Behavioral] Fix context item update test mocking paths`
