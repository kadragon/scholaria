# Research: Inline Editing + Optimistic UI

## Goal
Enable inline editing of Topic/Context names in list view with optimistic updates.

## Scope
- Click name cell to edit inline
- Save on blur / Enter key
- Cancel on Escape
- Optimistic UI: Update local state immediately, revert on error
- Use Refine's `useUpdate` with `optimisticUpdateMap`

## Related Files/Flows
- `frontend/src/pages/topics/list.tsx:182-196` - Topic name TableCell
- `frontend/src/pages/contexts/list.tsx:252-266` - Context name TableCell
- Refine `useUpdate` hook - supports `mutationOptions.optimisticUpdateMap`

## Evidence
1. **Current state**: Name cells are read-only `<TableCell>{topic.name}</TableCell>`
2. **Refine support**: `useUpdate` has built-in optimistic update support via `queryClient.setQueryData`
3. **Input component**: Can use `<Input>` from shadcn/ui

## Hypotheses
1. **Implementation**:
   - Add state: `editingId`, `editingValue`
   - Double-click name → show `<Input>`
   - Blur/Enter → call `useUpdate` with optimistic config
   - Escape → cancel edit
2. **Optimistic update**: Use Refine's `onMutate` to update cache immediately

## Assumptions/Open Qs
- **Q**: Should we allow editing description too?
  - **A**: **No** - only name (simpler, most common use case)
- **Q**: Should we debounce save?
  - **A**: **No** - save on blur/Enter (explicit action)

## Risks
- **Race conditions**: Multiple rapid edits → use `isMutating` check
- **Validation**: Backend may reject invalid names → show error toast

## Next
1. Create inline edit component (reusable)
2. Integrate into TopicList
3. Integrate into ContextList
4. Test optimistic updates + error rollback
