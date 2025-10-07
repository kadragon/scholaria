# Research

## Goal
Compact `docs/agents/TASKS.md` while keeping actionable context, and surface new candidate tasks worth pursuing next.

## Scope
- `docs/agents/TASKS.md`
- `docs/agents/AGENTS.md`
- `frontend/README.md`
- `backend/schemas/admin.py`

## Related Files/Flows
- Task management docs drive backlog visibility.
- Frontend README TODO list highlights missing admin UI updates.
- Admin schemas still lack datetime serializers noted in AGENTS backlog.

## Hypotheses
1. Current `TASKS.md` duplicates completed work; compressing sections will improve scanability without losing history.
2. Frontend README TODO entries are outdated because UI tasks were completed; aligning documentation is a useful follow-up task.
3. Admin Pydantic schemas missing ISO serializers remain an open gap and should be tracked as a backlog item.

## Evidence
- `docs/agents/TASKS.md` lists many `[x]` completed subtasks with verbose descriptions.
- `frontend/README.md` still lists unchecked TODOs for shadcn/ui integration and context CRUD despite related tasks being marked complete elsewhere.
- `backend/schemas/admin.py` defines `AdminTopicOut`/`AdminContextOut` without `@field_serializer` for datetimes, matching AGENTS backlog note.

## Assumptions / Open Questions
- Compression should retain high-level milestone history but detailed breakdown can move to archive references.
- No new high-priority tasks exist outside identified documentation gaps; confirm during planning.

## Sub-agent Findings
- None.

## Risks
- Over-compaction could hide necessary guidance for onboarding; mitigate by keeping high-level status bullets.
- Adding backlog items without estimating scope may create noise; ensure tasks are concrete and testable.

## Next
Draft execution plan (targets, steps, validation) before editing files.
