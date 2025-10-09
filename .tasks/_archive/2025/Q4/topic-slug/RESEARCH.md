# Research: Topic Slug Feature

## Goal
Add unique URL-friendly slug to Topic model for use in shareable links (e.g., "코러스" → "korus").

## Scope
- Backend: `Topic` model, schemas, routers, migration
- Frontend: Update routing to support slug-based URLs
- No existing slug/transliteration logic in codebase

## Related Files/Flows

### Backend
- **backend/models/topic.py:18-48** — `Topic` model (id, name, description, system_prompt, timestamps)
- **backend/schemas/topic.py:13-34** — `TopicBase`, `TopicOut` schemas
- **backend/routers/topics.py:17-47** — `GET /topics`, `GET /topics/{topic_id}`
- **alembic/versions/** — 2 existing migrations (0001_baseline, feedback_score)

### Frontend
- **frontend/src/pages/topics/list.tsx** — Topic list UI (uses `topic.id` for edit/delete)
- **frontend/src/pages/chat/hooks/useChat.ts:81** — Chat uses `topic_id` numeric
- **frontend/src/App.tsx** — Routes: `/admin/topics/edit/:id`

## Hypotheses
1. Add `slug` column (String, unique, indexed) to `rag_topic` table
2. Generate slug on Topic creation/update using Korean→Latin transliteration
3. Support both `/topics/{id}` and `/topics/slug/{slug}` endpoints for backward compatibility
4. Frontend can optionally use slug in URLs

## Evidence
- No existing slug/transliteration utilities found in codebase
- Current routing uses numeric IDs exclusively
- Topic name is user-editable (line 77-101 in list.tsx) → slug must update on name change

## Assumptions/Open Questions
- **Q:** Auto-generate slug from name, or allow manual override?
  **A:** Auto-generate with uniqueness enforcement (append `-2`, `-3` on collision)
- **Q:** Update slug when name changes?
  **A:** Yes, but preserve old slugs for backward compatibility (future enhancement)
- **Q:** Korean transliteration library?
  **A:** Use simple romanization (hangul-romanize, or manual mapping)

## Sub-agent Findings
- N/A

## Risks
1. **Unique constraint violation** if slug generation produces duplicates → handle with suffix
2. **Migration on prod** requires backfill for existing topics
3. **Breaking change** if frontend assumes numeric ID only → keep ID-based routes

## Next
Proceed to PLAN phase
