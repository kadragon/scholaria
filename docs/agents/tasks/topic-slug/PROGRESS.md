# Progress: Topic Slug Feature

## Summary
✅ **COMPLETED** — URL-friendly slug added to Topic model for shareable links.

## Goal & Approach
- TDD approach: test → implement → refactor
- Auto-generate slug from topic name with uniqueness enforcement
- Maintain backward compatibility with numeric ID routes

## Completed Steps
1. ✅ Research phase — analyzed codebase, identified affected files
2. ✅ Plan phase — outlined steps, test cases, rollback strategy
3. ✅ Created task artifacts
4. ✅ Implemented slug generation utility with Korean romanization
5. ✅ Added slug field to Topic model with auto-generation
6. ✅ Updated schemas to include slug
7. ✅ Added `GET /topics/slug/{slug}` endpoint
8. ✅ Created migration with backfill logic
9. ✅ All tests passing (40 topic/slug tests)
10. ✅ Lint and type checks clean
11. ✅ Committed: `9fdf043`

## Current Failures
- None

## Decision Log
- **Slug generation strategy:** Auto-generate from name, append `-N` on collision
- **Romanization:** Used `korean-romanizer` library (0.28.0) for reliable Korean→Latin conversion
- **Backward compat:** Kept ID-based routes, added new slug-based route
- **Auto-generation:** Used SQLAlchemy `@event.listens_for` on `before_insert` to auto-generate slugs

## Files Changed
- `backend/models/topic.py` — Added slug field + auto-generation event
- `backend/schemas/topic.py` — Added slug to schemas
- `backend/routers/topics.py` — Added `/topics/slug/{slug}` endpoint
- `backend/services/slug_utils.py` — New utility for slug generation
- `alembic/versions/0002_add_topic_slug.py` — Migration with backfill
- `pyproject.toml` — Added `korean-romanizer` dependency
- Tests: `test_slug_utils.py`, `test_topic_slug_routes.py`

## Next Step
Feature complete. Ready for merge.
