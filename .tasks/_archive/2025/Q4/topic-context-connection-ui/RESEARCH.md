# Research: Topic-Context Connection UI

## Goal
Add bidirectional UI for managing N:N relationships between Topics and Contexts

## Scope
- Topic edit page: select/unselect contexts
- Context edit page: select/unselect topics
- Real-time sync with backend

## Related Files/Flows

### Backend (already complete)
- `backend/models/associations.py:8` - `topic_context_association` table
- `backend/models/topic.py:34` - `contexts` relationship
- `backend/models/context.py:48` - `topics` relationship
- `backend/routers/admin/topics.py` - Topic CRUD with context management
- `backend/routers/admin/contexts.py` - Context CRUD with topic management

### Frontend (partial)
- `frontend/src/pages/contexts/list.tsx:75-115` - Bulk assign contexts → topic (exists)
- `frontend/src/pages/topics/edit.tsx` - Topic edit (missing context selection)
- `frontend/src/pages/contexts/edit.tsx` - Context edit (missing topic selection)

## Hypotheses
1. Backend already supports `contexts` array in Topic update payload
2. Backend already supports `topics` array in Context update payload
3. Need multi-select component for both edit pages
4. Refine's `useOne` should include related entities

## Evidence

### Backend API Support
Checking if admin endpoints handle relationship updates:

**Topics endpoint:**
- `backend/routers/admin/topics.py` - needs verification
- Expected: PATCH `/admin/topics/{id}` accepts `context_ids: list[int]`

**Contexts endpoint:**
- `backend/routers/admin/contexts.py` - needs verification
- Expected: PATCH `/admin/contexts/{id}` accepts `topic_ids: list[int]`

### Frontend Data Loading
- `frontend/src/pages/topics/edit.tsx:12` - uses `useOne` for topic data
- `frontend/src/pages/contexts/edit.tsx:12` - uses `useOne` for context data
- Need to verify if relationships are included in responses

## Assumptions/Open Questions
- ✅ N:N models already exist
- ✅ Bulk assign API exists (`/admin/bulk/assign-context-to-topic`)
- ❓ Do individual CRUD endpoints support relationship updates?
- ❓ Does `useOne` response include related entity IDs?
- ❓ Need new endpoints or can reuse existing update endpoints?

## Risks
- Low: Backend models already complete
- Medium: May need to add `context_ids`/`topic_ids` to update schemas
- Low: UI component complexity (multi-select is standard)

## Next
Verify backend schema support → Plan implementation strategy
