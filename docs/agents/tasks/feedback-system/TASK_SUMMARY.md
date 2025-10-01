# Task Summary: Feedback System (좋아요/싫어요)

## Goal
Q&A 히스토리에 좋아요/싫어요 피드백 기능 추가

## Key Changes

### Files Modified
- `backend/models/history.py` - `feedback_score: Mapped[int]` 필드 추가
- `backend/schemas/history.py` - `FeedbackRequest` 스키마 + `QuestionHistoryOut` 확장
- `backend/routers/history.py` - PATCH `/api/history/{id}/feedback` 엔드포인트
- `alembic/versions/990a42024f17_add_feedback_score.py` - DB 마이그레이션

### Files Created
- `backend/tests/test_feedback.py` - 6개 테스트 케이스

## Tests
- ✅ 6/6 passing: like/dislike/neutral, validation (422), not found (404), GET integration
- ✅ mypy strict mode
- ✅ ruff clean

## Commits
- Migration: `990a42024f17`
- Implementation: (pending commit)

## Notes
- Default feedback_score: 0 (neutral)
- Validation: -1 (dislike) / 0 (neutral) / 1 (like)
- Frontend UI deferred to separate task
