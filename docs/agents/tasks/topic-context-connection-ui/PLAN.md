# Plan: Topic-Context Connection UI

## Objective
Add multi-select UI for bidirectional Topic↔Context relationship management in edit pages

## Constraints
- Backend already supports `context_ids` in `AdminTopicUpdate` (`backend/schemas/admin.py:37`)
- Backend **does NOT** support `topic_ids` in `AdminContextUpdate` (needs to be added)
- Must maintain existing functionality (no breaking changes)
- Use shadcn/ui components for consistency

## Target Files & Changes

### Backend (Schema + Router)

1. **`backend/schemas/admin.py`**
   - Add `topic_ids: list[int] | None = None` to `AdminContextUpdate` class

2. **`backend/routers/admin/contexts.py:115-155`**
   - Update `update_context` function to handle `topic_ids` field (similar to topics router)

3. **`backend/routers/admin/topics.py:83-95`**
   - Already handles `context_ids` correctly ✅ (no changes needed)

### Frontend (Edit Pages)

4. **`frontend/src/pages/topics/edit.tsx`**
   - Add `useList` to fetch all contexts
   - Add multi-select component for context selection
   - Include `context_ids` in update payload
   - Load existing context relationships from topic data

5. **`frontend/src/pages/contexts/edit.tsx`**
   - Add `useList` to fetch all topics
   - Add multi-select component for topic selection
   - Include `topic_ids` in update payload
   - Load existing topic relationships from context data

6. **`frontend/src/components/ui/multi-select.tsx`** (NEW)
   - Create reusable multi-select component using shadcn/ui primitives
   - Use Command + Popover pattern (similar to combobox)

### Backend Response Schema Enhancement

7. **`backend/schemas/admin.py:59-68`** (`AdminContextOut`)
   - Add `topics_count: int` field (parallel to `AdminTopicOut.contexts_count`)

8. **`backend/routers/admin/contexts.py:78-92, 103-116, 129-147`**
   - Add `topics_count` to all `AdminContextOut` responses

9. **`backend/routers/admin/topics.py:81-95`**
   - Enhance `get_topic` response to include `context_ids: list[int]`

10. **`backend/routers/admin/contexts.py:78-92`**
    - Enhance `get_context` response to include `topic_ids: list[int]`

## Test/Validation Cases

### Backend Tests
- [ ] `AdminContextUpdate` accepts `topic_ids` field
- [ ] `PATCH /admin/contexts/{id}` with `topic_ids` updates relationships
- [ ] Context GET response includes `topic_ids` and `topics_count`
- [ ] Topic GET response includes `context_ids`

### Frontend Tests (Manual)
- [ ] Topic edit page displays existing contexts as selected
- [ ] Topic edit page can add/remove contexts
- [ ] Context edit page displays existing topics as selected
- [ ] Context edit page can add/remove topics
- [ ] Multi-select component is keyboard accessible
- [ ] Changes persist after save

## Steps

### Phase 1: Backend Schema & Endpoints
1. Update `AdminContextUpdate` schema with `topic_ids`
2. Update `AdminContextOut` schema with `topics_count`
3. Update `update_context` router to handle `topic_ids`
4. Update context router responses to include `topics_count` and `topic_ids`
5. Update topic router `get_topic` to include `context_ids`
6. Write tests for new schema fields and relationship updates

### Phase 2: Frontend Multi-Select Component
7. Create `multi-select.tsx` component
8. Test component in isolation

### Phase 3: Topic Edit Page
9. Integrate multi-select for contexts in topic edit
10. Load existing context IDs from topic data
11. Update payload to include `context_ids`

### Phase 4: Context Edit Page
12. Integrate multi-select for topics in context edit
13. Load existing topic IDs from context data
14. Update payload to include `topic_ids`

### Phase 5: Testing & Validation
15. Manual E2E test: create topic → assign contexts → verify
16. Manual E2E test: edit context → assign topics → verify
17. Verify bidirectional sync (topic.contexts ↔ context.topics)

## Rollback
If issues arise:
1. Phase 1: Revert schema/router changes (backend isolated)
2. Phase 2-4: Remove frontend components (no backend dependency)
3. Full rollback: `git revert <commit-sha>`

## Review Hotspots
- **Backend:** `topic_ids` relationship update logic in contexts router
- **Frontend:** Multi-select state management and payload construction
- **UX:** Clear indication of current selections + search/filter for large lists
