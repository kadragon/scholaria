# Plan: Inline Editing + Optimistic UI

## Objective
Add inline editing for Topic/Context names with optimistic updates.

## Constraints
- Use Refine's `useUpdate` hook
- Optimistic updates via `onMutate` + `queryClient.setQueryData`
- No new dependencies
- Reusable component pattern

## Target Files & Changes

### 1. **New: `frontend/src/components/InlineEditCell.tsx`**
- Reusable inline edit component
- Props: `value`, `onSave`, `resource`, `id`
- State: `isEditing`, `editValue`
- Handles Enter/Escape/Blur

### 2. **Edit: `frontend/src/pages/topics/list.tsx`**
- Replace name `<TableCell>` with `<InlineEditCell>`
- Use `useUpdate` for optimistic updates
- Handle success/error toasts

### 3. **Edit: `frontend/src/pages/contexts/list.tsx`**
- Same pattern as topics

## Test/Validation Cases
1. **Double-click name**: Shows input field
2. **Enter key**: Saves and reverts to display
3. **Escape key**: Cancels without saving
4. **Blur**: Saves changes
5. **Optimistic update**: Name changes immediately
6. **Error**: Reverts on backend failure + shows toast

## Steps
1. [ ] Create `InlineEditCell` component
2. [ ] Integrate into TopicList with optimistic update
3. [ ] Integrate into ContextList
4. [ ] Test edit/cancel/error flows
5. [ ] Run `npm run typecheck` + `npm run lint`

## Rollback
- Remove `InlineEditCell.tsx`
- Revert list files to read-only cells

## Review Hotspots
- **Optimistic updates**: Ensure cache update/revert works correctly
- **Validation**: Handle backend errors gracefully

## Status
- [ ] Step 1: InlineEditCell component
- [ ] Step 2: TopicList integration
- [ ] Step 3: ContextList integration
- [ ] Step 4: Testing
- [ ] Step 5: Quality checks
