# Plan: Skeleton Loading States

## Objective
Replace text-based loading states with skeleton loaders.

## Constraints
- Tailwind CSS only (no new dependencies)
- Reusable components
- Match actual content structure

## Target Files & Changes

### 1. **New: `frontend/src/components/ui/skeleton.tsx`**
- Basic `<Skeleton>` component
- Props: `className`
- Default: `bg-gray-200 animate-pulse rounded`

### 2. **New: `frontend/src/components/TableSkeleton.tsx`**
- Skeleton table with configurable rows/columns
- Mimics `<Table>` structure

### 3. **New: `frontend/src/components/AnalyticsSkeleton.tsx`**
- 4 stat card skeletons + 3 chart skeletons
- Matches Bento Grid layout

### 4. **Edit: `frontend/src/pages/topics/list.tsx`**
- Replace "로딩 중..." with `<TableSkeleton columns={6} rows={8} />`

### 5. **Edit: `frontend/src/pages/contexts/list.tsx`**
- Same pattern

### 6. **Edit: `frontend/src/pages/analytics.tsx`**
- Replace with `<AnalyticsSkeleton />`

## Test/Validation Cases
1. **Load TopicList**: Shows table skeleton
2. **Load ContextList**: Shows table skeleton
3. **Load Analytics**: Shows stat cards + chart skeletons
4. **Animation**: Pulse animation visible

## Steps
1. [ ] Create `Skeleton` primitive
2. [ ] Create `TableSkeleton`
3. [ ] Create `AnalyticsSkeleton`
4. [ ] Replace TopicList loading state
5. [ ] Replace ContextList loading state
6. [ ] Replace Analytics loading state
7. [ ] Run `npm run typecheck` + `npm run lint`

## Rollback
- Remove skeleton components
- Revert to "로딩 중..." text

## Review Hotspots
- **Animation performance**: Ensure no jank on low-end devices
- **Accessibility**: Skeleton should have `aria-label="로딩 중"`

## Status
- [ ] Step 1: Skeleton primitive
- [ ] Step 2: TableSkeleton
- [ ] Step 3: AnalyticsSkeleton
- [ ] Step 4-6: Replace loading states
- [ ] Step 7: Quality checks
