# Progress: Topic-Context Connection UI

## Summary
Adding bidirectional multi-select UI for Topic↔Context N:N relationship management

## Goal & Approach
- Backend: Add `topic_ids` support to Context update schema/router
- Frontend: Create multi-select component + integrate into edit pages
- Ensure bidirectional sync (topic.contexts ↔ context.topics)

## Completed Steps
- [x] Research: Verified N:N models exist, topics router supports `context_ids`
- [x] Plan: Identified missing `topic_ids` in contexts router, planned 15-step implementation
- [x] Phase 1: Backend schema & endpoints (Steps 1-6)
  - [x] Add `topic_ids` to `AdminContextUpdate`
  - [x] Add `topics_count` to `AdminContextOut`
  - [x] Update `update_context` to handle topic relationships
  - [x] Update all context responses to include `topics_count`
  - [x] Write 5 relationship tests (all passing)
- [x] Phase 2: Frontend multi-select component (Steps 7-8)
  - [x] Create `multi-select.tsx` with Command + Popover pattern
  - [x] Install missing shadcn components (command, popover, badge)
- [x] Phase 3: Topic edit page (Steps 9-11)
  - [x] Integrate multi-select for contexts
  - [x] Load existing context IDs from topic data
  - [x] Update payload to include `context_ids`
- [x] Phase 4: Context edit page (Steps 12-14)
  - [x] Integrate multi-select for topics
  - [x] Load existing topic IDs from context data
  - [x] Update payload to include `topic_ids`
- [x] All tests passing (148/148)
- [x] Frontend build successful

## Current Failures
None

## Decision Log
- Use shadcn/ui Command + Popover pattern for multi-select (consistent with existing UI)
- Add `topics_count` to `AdminContextOut` for symmetry with `AdminTopicOut.contexts_count`
- Include full ID lists in GET responses to enable edit page prefill

## Next Step
Phase 1: Backend schema & router updates (steps 1-6)
