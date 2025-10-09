# Plan: Data Table with Faceted Filters

## Objective
Add advanced filtering (type, status, search) to Context/Topic list pages.

## Constraints
- Client-side filtering only (no backend changes)
- Use existing Radix UI components
- Follow shadcn/ui data-table pattern
- Maintain existing bulk action functionality

## Target Files & Changes

### 1. **New: `frontend/src/components/ui/data-table-toolbar.tsx`**
- Props: `searchValue`, `onSearchChange`, `filters` (React nodes), `onReset`
- Layout: Search input + filters + reset button

### 2. **New: `frontend/src/components/ui/faceted-filter.tsx`**
- Multi-select filter with Popover + Checkbox list
- Props: `title`, `options` (value/label/icon), `selectedValues`, `onSelectedValuesChange`

### 3. **Edit: `frontend/src/pages/contexts/list.tsx`**
- Add state: `searchQuery`, `typeFilter`, `statusFilter`
- Add filtering logic: `filteredData = data?.data.filter(...)`
- Add `DataTableToolbar` component above table
- Pass `filteredData` to table

### 4. **Edit: `frontend/src/pages/topics/list.tsx`**
- Add state: `searchQuery`, `contextCountFilter`
- Add filtering logic
- Add `DataTableToolbar`

## Test/Validation Cases
1. **Search**: Type "test" → shows only items with "test" in name/description
2. **Type filter**: Select "PDF" + "FAQ" → shows only PDF/FAQ contexts
3. **Status filter**: Select "COMPLETED" → shows only completed contexts
4. **Combined filters**: Search "test" + Type "PDF" → shows only PDF contexts with "test"
5. **Reset**: Click reset → clears all filters

## Steps
1. [ ] Create `FacetedFilter` component
2. [ ] Create `DataTableToolbar` component
3. [ ] Refactor `ContextList` with filters
4. [ ] Refactor `TopicList` with filters
5. [ ] Manual test all filter combinations
6. [ ] Run `npm run typecheck` + `npm run lint`

## Rollback
- Remove `faceted-filter.tsx`, `data-table-toolbar.tsx`
- Revert `list.tsx` files to original state

## Review Hotspots
- **Filter logic**: Ensure case-insensitive search
- **State management**: Verify filter state updates correctly
- **UX**: Reset button clears all filters properly

## Status
- [ ] Step 1: FacetedFilter component
- [ ] Step 2: DataTableToolbar component
- [ ] Step 3: ContextList filters
- [ ] Step 4: TopicList filters
- [ ] Step 5: Manual testing
- [ ] Step 6: Quality checks
