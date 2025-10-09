# Plan: Feedback System (좋아요/싫어요)

## Objective
Add like/dislike feedback for Q&A history records via PATCH endpoint.

## Constraints
- TDD: Red → Green → Refactor
- Alembic migration for schema change
- mypy strict + ruff clean
- No frontend changes (backend-only for now)

## Target Files & Changes

### 1. Migration (New)
- `alembic/versions/XXXX_add_feedback_score.py`
- Add `feedback_score` INT DEFAULT 0

### 2. Model
- `backend/models/history.py`
- Add `feedback_score: Mapped[int]` field

### 3. Schema
- `backend/schemas/history.py`
- Add `FeedbackRequest(BaseModel)` with `feedback_score: int` (constrained -1/0/1)
- Add `feedback_score: int` to `QuestionHistoryOut`

### 4. Router
- `backend/routers/history.py`
- Add `PATCH /history/{history_id}/feedback` endpoint

### 5. Tests (New)
- `backend/tests/test_feedback.py`
- Test valid feedback (-1, 0, 1)
- Test invalid feedback (2, -2, etc.)
- Test 404 for nonexistent history_id
- Test feedback retrieval in GET /history

## Test/Validation Cases

1. **Migration**: Run `alembic upgrade head` without errors
2. **Model**: `feedback_score` defaults to 0
3. **Schema**: Pydantic validates -1/0/1 only
4. **Endpoint**:
   - PATCH with valid score → 200 + updated record
   - PATCH with invalid score → 422
   - PATCH with bad history_id → 404
   - GET /history includes `feedback_score`

## Steps

- [ ] **Step 1**: Write failing test for PATCH /history/{id}/feedback
- [ ] **Step 2**: Add FeedbackRequest schema with validation
- [ ] **Step 3**: Add PATCH endpoint (will fail on DB column)
- [ ] **Step 4**: Create Alembic migration for feedback_score
- [ ] **Step 5**: Add feedback_score to QuestionHistory model
- [ ] **Step 6**: Add feedback_score to QuestionHistoryOut schema
- [ ] **Step 7**: Update GET /history test to verify feedback_score
- [ ] **Step 8**: Run full test suite + mypy + ruff

## Rollback
- `alembic downgrade -1` to remove column
- Revert code changes via git

## Review Hotspots
- Schema validation: ensure only -1/0/1 accepted
- Migration: default value for existing records
- Endpoint auth: verify JWT protection (should inherit from router)

## Status
- [x] Step 1: test - 6 test cases written
- [x] Step 2: schema - FeedbackRequest added
- [x] Step 3: endpoint - PATCH /history/{id}/feedback
- [x] Step 4: migration - 990a42024f17_add_feedback_score
- [x] Step 5: model - feedback_score field added
- [x] Step 6: schema out - QuestionHistoryOut updated
- [x] Step 7: integration test - all 6 tests passing
- [x] Step 8: quality checks - mypy + ruff clean
