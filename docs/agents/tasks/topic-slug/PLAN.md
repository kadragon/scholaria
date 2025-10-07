# Plan: Topic Slug Feature

## Objective
Add URL-friendly slug to Topic model with auto-generation from name (e.g., "코러스" → "korus").

## Constraints
- Maintain backward compatibility with numeric ID-based routes
- Slug must be unique, indexed, URL-safe
- Existing topics need slug backfill in migration

## Target Files & Changes

### 1. Model & Schema
- **backend/models/topic.py** — Add `slug: Mapped[str]` field (unique, indexed)
- **backend/schemas/topic.py** — Add `slug: str` to `TopicBase` and `TopicOut`

### 2. Slug Generation Utility
- **backend/services/slug_utils.py** (new) — `generate_slug(name: str) -> str`, `ensure_unique_slug(base_slug: str, db: Session) -> str`

### 3. Migration
- **alembic/versions/XXXX_add_topic_slug.py** (new) — Add column, backfill existing topics, add unique constraint

### 4. Routers
- **backend/routers/topics.py** — Add `GET /topics/slug/{slug}` endpoint
- **backend/routers/admin/topics.py** (if exists, check) — Update create/edit to handle slug generation

### 5. Tests
- **backend/tests/test_topic_slug.py** (new) — Test slug generation, uniqueness, retrieval, Korean/English/mixed inputs

## Test/Validation Cases
1. **Slug generation**
   - Korean "코러스" → "korus"
   - English "AI Chat" → "ai-chat"
   - Mixed "AI 챗봇" → "ai-chaetbot"
   - Special chars "Hello@World!" → "hello-world"
2. **Uniqueness**
   - Duplicate name → slug gets `-2`, `-3` suffix
3. **Retrieval**
   - `GET /topics/slug/korus` returns correct topic
   - `GET /topics/1` still works (backward compat)
4. **Migration**
   - Existing topics get unique slugs after migration

## Steps
1. [x] Research & Plan
2. [ ] Write test for slug generation utility (TDD)
3. [ ] Implement slug generation utility
4. [ ] Write test for Topic model with slug
5. [ ] Add slug field to Topic model
6. [ ] Update schemas to include slug
7. [ ] Write test for slug-based retrieval endpoint
8. [ ] Add `GET /topics/slug/{slug}` route
9. [ ] Write migration with backfill logic
10. [ ] Run migration in dev environment
11. [ ] Verify all tests pass
12. [ ] (Optional) Update frontend to use slug in URLs

## Rollback
- Revert migration: `alembic downgrade -1`
- Drop column manually: `ALTER TABLE rag_topic DROP COLUMN slug;`

## Review Hotspots
- **Slug collision handling** — ensure uniqueness without race conditions
- **Korean romanization** — verify output is readable and URL-safe
- **Migration backfill** — test with realistic topic names

## Status
- [x] Step 1: Research & Plan
- [ ] Step 2: TDD slug generation utility
