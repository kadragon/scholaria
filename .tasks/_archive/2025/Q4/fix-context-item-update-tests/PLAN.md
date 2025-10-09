# Plan: Fix Context Item Update Tests

## Objective
3개의 실패한 테스트를 수정하여 실제 구현과 일치하도록 함

## Constraints
- TDD 원칙 유지 (Red → Green)
- 테스트 의도 보존
- 기존 통과 테스트 영향 없음

## Target Files & Changes

### `backend/tests/admin/test_admin_contexts.py`
- **Line 238-240**: `test_update_context_item_validation_empty_content`
  - 변경: `backend.routers.contexts.EmbeddingService` → `backend.tasks.embeddings.regenerate_embedding_task`
- **Line 276-278**: `test_update_context_item_content_success`
  - 변경: 동일한 모킹 경로 수정
- **Line 323-325**: `test_update_context_item_embedding_regeneration`
  - 변경: 동일한 모킹 경로 수정 + `.delay()` 호출 검증으로 변경

### 실제 구현 (참고용)
- `backend/routers/contexts.py:290` - `regenerate_embedding_task.delay(item.id)` 호출

## Test/Validation Cases
1. 3개 테스트 모두 통과
2. 기존 131개 테스트 여전히 통과
3. 테스트 의도 유지 (validation, content update, embedding regeneration trigger)

## Steps
1. [x] Research - 실패 원인 파악 (AttributeError)
2. [ ] Implement - 테스트 모킹 경로 수정
3. [ ] Validate - 전체 테스트 재실행
4. [ ] Commit - [Behavioral] 커밋

## Rollback
- Git revert 가능 (테스트 파일만 수정)

## Review Hotspots
- 테스트가 Celery task 호출을 제대로 검증하는지 확인
- `test_update_context_item_embedding_regeneration`에서 `.delay()` 호출 검증 필요

## Status
- [x] Step 1: Research
- [ ] Step 2: Fix test mocking paths
- [ ] Step 3: Run full test suite
- [ ] Step 4: Commit
