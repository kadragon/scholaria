# Progress: Fix Context Item Update Tests

## Summary
3개 실패 테스트를 수정하여 전체 134개 테스트 통과

## Goal & Approach
- 테스트가 모킹하는 경로를 실제 구현과 일치시킴
- `backend.routers.contexts.EmbeddingService` → `backend.tasks.embeddings.regenerate_embedding_task`

## Completed Steps
1. ✅ 실패 원인 파악 - `AttributeError: module has no attribute 'EmbeddingService'`
2. ✅ 실제 구현 확인 - `backend.routers.contexts.py:290`에서 `regenerate_embedding_task.delay()` 호출
3. ✅ 3개 테스트 모킹 경로 수정 (line 238, 275, 321)
4. ✅ 전체 테스트 재실행 - 134 passed

## Current Failures
None

## Decision Log
- **모킹 대상 변경**: 라우터는 `EmbeddingService`를 직접 사용하지 않고 Celery task를 호출하므로, 테스트도 task를 모킹해야 함
- **검증 방식 변경**: `test_update_context_item_embedding_regeneration`에서 `mock_task.delay.assert_called_once_with(item_id)` 사용

## Next Step
커밋 준비
