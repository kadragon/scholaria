# Task Summary: Topic-Context Connection UI

## Goal
Add bidirectional multi-select UI for managing N:N Topic↔Context relationships in edit pages

## Key Changes

### Backend (`backend/`)
- **schemas/admin.py:59-68** - Added `topics_count: int` to `AdminContextOut`
- **schemas/admin.py:89** - Added `topic_ids: list[int] | None` to `AdminContextUpdate`
- **routers/admin/contexts.py:136-170** - Updated `update_context` to handle `topic_ids` relationship
- **routers/admin/contexts.py:62,93,164** - Added `topics_count=len(ctx.topics)` to all responses
- **tests/admin/test_context_topic_relationships.py** - New file with 5 relationship tests

### Frontend (`frontend/src/`)
- **components/ui/multi-select.tsx** - New reusable multi-select component (Command + Popover pattern)
- **pages/topics/edit.tsx:7-8** - Added `useList` for contexts + `MultiSelect` import
- **pages/topics/edit.tsx:22-26** - Added `contextIds` state + contexts data loading
- **pages/topics/edit.tsx:29-34** - Load existing context IDs from topic data
- **pages/topics/edit.tsx:43** - Include `context_ids` in update payload
- **pages/topics/edit.tsx:90-103** - Added multi-select UI for contexts
- **pages/contexts/edit.tsx** - Same pattern for topic selection

## Tests
- **148 tests passing** (5 new relationship tests)
- `test_update_context_with_topic_ids` - Add topics to context
- `test_update_context_remove_topics` - Remove all topics
- `test_list_contexts_includes_topics_count` - List response includes count
- `test_get_context_includes_topics_count` - Get response includes count
- `test_get_topic_contexts_count` - Topic GET shows contexts_count

## Commit SHAs
(To be added after commit)

## Notes
- Backend already supported `context_ids` in topics; added symmetric `topic_ids` for contexts
- Multi-select uses shadcn/ui primitives (Command, Popover, Badge)
- Bidirectional sync: updating topic.contexts automatically updates context.topics (SQLAlchemy relationship)
