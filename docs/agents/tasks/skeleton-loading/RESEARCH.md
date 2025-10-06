# Research: Skeleton Loading States

## Goal
Replace generic "로딩 중..." text with skeleton loaders that mimic content structure.

## Scope
- **Target pages**: TopicList, ContextList, Analytics
- Skeleton shapes match actual content (cards, table rows, charts)
- Tailwind-based implementation (no new deps)

## Related Files/Flows
- `frontend/src/pages/topics/list.tsx:44` - "로딩 중..." state
- `frontend/src/pages/contexts/list.tsx:48` - "로딩 중..." state
- `frontend/src/pages/analytics.tsx:93` - "로딩 중..." state

## Evidence
1. **Current loading states**: Simple text div `<div className="p-6">로딩 중...</div>`
2. **Tailwind skeleton pattern**:
   - `bg-gray-200 animate-pulse rounded`
   - Stack multiple divs to mimic structure

## Hypotheses
1. **Skeleton types needed**:
   - **Table rows**: 5-10 skeleton rows with cell-width divs
   - **Analytics cards**: 4 skeleton stat cards + 3 chart placeholders
2. **Implementation**: Create reusable skeleton components

## Assumptions/Open Qs
- **Q**: Should we use a library like `react-loading-skeleton`?
  - **A**: **No** - Tailwind-only (simpler, no bundle size increase)
- **Q**: How many skeleton rows?
  - **A**: **8 rows** (representative of typical list length)

## Risks
- **Over-engineering**: Skeleton complexity → use simple shapes only

## Next
1. Create `Skeleton` primitive component
2. Create `TableSkeleton` component
3. Create `AnalyticsSkeleton` component
4. Replace loading states
