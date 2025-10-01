# Research: Feedback System (좋아요/싫어요)

## Goal
Add like/dislike feedback mechanism for RAG Q&A responses.

## Scope
- Feedback on **QuestionHistory** records (already has `is_favorited` field)
- Add `feedback_score` field: -1 (dislike), 0 (neutral), 1 (like)
- Expose feedback endpoint: `PATCH /history/{id}/feedback`
- Update frontend to display/submit feedback

## Related Files/Flows

### Backend Models
- `backend/models/history.py` - QuestionHistory model (has `is_favorited`, needs `feedback_score`)
- `backend/schemas/history.py` - QuestionHistoryOut schema
- `backend/routers/history.py` - Read-only history router
- `backend/routers/rag.py:50-118` - `ask_question()` creates QuestionHistory

### Frontend
- `frontend/src/pages/*` - Refine-based admin UI
- No history display UI exists yet (only RAG interaction)

### Database
- Migration needed for new `feedback_score` column

## Hypotheses

1. **Minimal scope**: Add `feedback_score` to QuestionHistory, expose PATCH endpoint
2. **Frontend**: Admin panel may not be the right place (user-facing feature)
3. **Migration**: Add nullable int column with default 0

## Evidence

- `QuestionHistory.is_favorited` exists but unused (star/favorite != like/dislike)
- Current flow: `rag.py:ask_question()` → creates `QuestionHistory` → no frontend display
- `test_history_read.py` is skipped (Django ORM remnant)

## Assumptions/Open Qs

- **Q**: Should feedback be separate from `is_favorited`?
  **A**: Yes, different semantics (favorite vs quality rating)
- **Q**: Frontend display location?
  **A**: Likely needs dedicated chat history UI (out of scope for this task)
- **Q**: Analytics/aggregation?
  **A**: Not needed for MVP (just store raw scores)

## Sub-agent Findings
N/A (straightforward task)

## Risks

- **Low**: Simple CRUD operation on existing model
- **Migration**: Need to handle existing records (default to 0)
- **Frontend**: May defer UI implementation to separate task

## Next
Write PLAN.md with TDD approach.
