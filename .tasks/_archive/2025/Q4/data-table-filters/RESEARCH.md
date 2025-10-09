# Research: Data Table with Faceted Filters

## Goal
Enhance Topic/Context list pages with advanced filtering (type, status, search) + sorting + pagination.

## Scope
- **Contexts list**: Filter by `context_type` (PDF/FAQ/Markdown), `processing_status` (PENDING/PROCESSING/COMPLETED/FAILED)
- **Topics list**: Filter by existence of contexts (has/no contexts)
- Search input for name/description
- Column sorting
- shadcn/ui data-table pattern

## Related Files/Flows
- `frontend/src/pages/contexts/list.tsx:1-264` - Context list (basic table)
- `frontend/src/pages/topics/list.tsx:1-246` - Topic list (basic table)
- `backend/schemas/context.py:35-41` - `context_type`, `processing_status` fields
- `frontend/src/components/ui/table.tsx` - shadcn/ui Table component
- `frontend/package.json:11-14` - Radix UI Select, Popover already installed

## Evidence
1. **Current implementation**: Basic `<Table>` with manual checkboxes + bulk actions
2. **Available fields for filtering**:
   - **Context**: `context_type` (string), `processing_status` (string), `name` (string)
   - **Topic**: `name` (string), `contexts_count` (number)
3. **No existing filtering**: Lists show all items, no search/filter UI

## Hypotheses
1. **Filter placement**: Add toolbar above table with:
   - Search input (left)
   - Faceted filters (center): Multi-select for type/status
   - Reset button (right)
2. **Implementation**:
   - Client-side filtering (current data is fully loaded)
   - Use `Array.filter()` on `data?.data`
3. **UI components**: Use Radix `Popover` + `Checkbox` for multi-select filters

## Assumptions/Open Qs
- **Q**: Should we add server-side filtering (backend API changes)?
  - **A**: Start **client-side only** (simpler, no backend changes). Can add server-side later.
- **Q**: Should we add pagination?
  - **A**: **No** for now (lists are typically <100 items). Add later if needed.

## Risks
- **Performance**: Large lists (>500 items) may lag with client-side filtering
  - **Mitigation**: Current data shows ~10-50 items → acceptable

## Next
1. Create reusable `DataTableToolbar` component
2. Create `FacetedFilter` component (multi-select popover)
3. Refactor `ContextList` with filters
4. Refactor `TopicList` with filters
