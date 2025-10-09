# Plan

## Objective
Produce a concise `docs/agents/TASKS.md` highlighting current status and actionable backlog, including newly identified tasks from research.

## Constraints
- Preserve essential context on project readiness and key backlogs.
- Follow documentation retention policy (no unnecessary deletions beyond compaction).
- Keep formatting simple for quick CLI scanning.

## Target Files & Changes
- `docs/agents/TASKS.md`: restructure sections, trim completed lists, add concise backlog items.

## Test / Validation Cases
- Manual review: file reads clearly in <1 screen per section and lists actionable tasks with checkboxes.

## Steps
1. Draft compact outline for `TASKS.md` (section order, bullets).
2. Apply edits to `docs/agents/TASKS.md` following outline.
3. Insert new backlog tasks (frontend README update, admin datetime serializers) with brief details.
4. Final read-through ensuring links/paths remain accurate.
5. Add backlog entry covering PostgreSQL & Qdrant backup/restore process.
6. Perform final verification after backlog expansion.

## Rollback
Restore previous version via git (`git checkout -- docs/agents/TASKS.md`) if the new layout is unsatisfactory.

## Review Hotspots
- Ensure no loss of critical milestone references.
- Verify new backlog tasks are specific and scoped.

## Status
- [x] Step 1 — Outline
- [x] Step 2 — Apply edits
- [x] Step 3 — Add initial backlog items
- [x] Step 4 — Review updated structure
- [x] Step 5 — Add backup/restore backlog entry
- [x] Step 6 — Final verification
