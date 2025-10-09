# Progress: Feedback System (좋아요/싫어요)

## Summary
✅ **완료**: Q&A 히스토리에 좋아요/싫어요 피드백 시스템 추가

## Goal & Approach
- `QuestionHistory` 모델에 `feedback_score` 필드 추가 (-1/0/1)
- PATCH `/api/history/{id}/feedback` 엔드포인트 구현
- TDD 방식으로 테스트 먼저 작성 후 구현

## Completed Steps

### ✅ Step 1: Test-first (Red)
- `backend/tests/test_feedback.py` 생성
- 6개 테스트 케이스 작성:
  - PATCH like/dislike/neutral
  - 422 for invalid score (not -1/0/1)
  - 404 for nonexistent history_id
  - GET includes feedback_score

### ✅ Step 2: Schema
- `backend/schemas/history.py`:
  - `FeedbackRequest` 추가 (score -1/0/1 validation)
  - `QuestionHistoryOut`에 `feedback_score` 필드 추가

### ✅ Step 3: Endpoint
- `backend/routers/history.py`:
  - PATCH `/history/{history_id}/feedback` 구현
  - 404 handling for missing records

### ✅ Step 4: Migration
- Alembic migration `990a42024f17_add_feedback_score`
- `rag_questionhistory.feedback_score` INT DEFAULT 0 추가

### ✅ Step 5: Model
- `backend/models/history.py`:
  - `feedback_score: Mapped[int]` 필드 추가 (default=0)

### ✅ Step 6: Quality checks
- ✅ All 6 feedback tests passing
- ✅ mypy: Success (no issues)
- ✅ ruff: Fixed whitespace issues

## Current Failures
None (pre-existing test failure in `test_admin_contexts.py` unrelated to this task)

## Decision Log
1. **Default value**: 0 (neutral) for existing records
2. **Validation**: Pydantic constraint `ge=-1, le=1`
3. **Frontend**: Deferred to separate task (backend-only for now)

## Next Step
✅ Task complete - update TASKS.md and commit
