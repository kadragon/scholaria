# Plan: Bento Grid Layout

## Objective
Refactor Analytics page with modern Bento Grid layout (asymmetric, variable-sized cards).

## Constraints
- Maintain all existing data/charts
- Responsive (mobile stack, desktop grid)
- Use Tailwind CSS Grid utilities only
- No new dependencies

## Target Files & Changes

### 1. **Edit: `frontend/src/pages/analytics.tsx`**
- Change summary grid from `grid-cols-4` to Bento layout:
  - Desktop: 6-column grid with variable col/row spans
  - Mobile: Single column stack
- Add card hover effects (scale + shadow)
- Adjust chart container spans for visual hierarchy

**Layout structure (desktop 6-col grid)**:
```
Row 1: [Summary1 (2col)] [Summary2 (2col)] [Trend (2col, 2row)]
Row 2: [Summary3 (2col)] [Summary4 (2col)] [Trend cont.]
Row 3: [Topics (3col)]   [Feedback (3col)]
```

## Test/Validation Cases
1. **Desktop**: Cards arranged in asymmetric grid
2. **Mobile**: Cards stack vertically
3. **Hover**: Cards scale slightly on hover
4. **Data**: All charts render correctly

## Steps
1. [ ] Refactor summary grid (6-column Bento layout)
2. [ ] Adjust chart containers with col/row spans
3. [ ] Add hover transitions
4. [ ] Test responsive breakpoints
5. [ ] Run `npm run typecheck` + `npm run lint`

## Rollback
- Revert `analytics.tsx` to original grid layout

## Review Hotspots
- **Grid alignment**: Ensure no layout breaks on edge cases (empty data)
- **Responsive**: Mobile must stack cleanly

## Status
- [ ] Step 1: Bento grid structure
- [ ] Step 2: Chart container spans
- [ ] Step 3: Hover effects
- [ ] Step 4: Responsive testing
- [ ] Step 5: Quality checks
