# Research: Bento Grid Layout

## Goal
Modernize Analytics dashboard with Bento Grid layout - variable-sized cards in asymmetric grid pattern.

## Scope
- Refactor Analytics page from 2-column grid to Bento-style layout
- Responsive design (mobile: stack, desktop: complex grid)
- Maintain all existing charts (Line, Bar, Pie)

## Related Files/Flows
- `frontend/src/pages/analytics.tsx:1-241` - Current analytics page (4-stat summary + 3 charts)
- `frontend/package.json:27` - recharts@3.2.1 for charts

## Evidence
1. **Current layout**: Standard grid (`grid-cols-1 md:grid-cols-4`, `md:grid-cols-2`)
2. **Components**:
   - 4 summary cards (총 질문 수, 피드백 수, 활성 세션, 평균 점수)
   - Line chart (질문 추세)
   - Bar chart (토픽별 활동)
   - Pie chart (피드백 분포)

## Hypotheses
1. **Bento Grid pattern**: Use CSS Grid with `grid-template-areas` for named layout regions
2. **Responsive**: Mobile stacks, desktop uses asymmetric areas
3. **Example layout** (desktop):
   ```
   [summary1] [summary2] [trend  ]
   [summary3] [summary4] [trend  ]
   [topics  ] [topics  ] [feedback]
   ```

## Assumptions/Open Qs
- **Q**: Should we add hover effects / card animations?
  - **A**: Yes - subtle scale on hover, smooth transitions
- **Q**: Should summary cards be merged?
  - **A**: No - keep 4 separate for clarity

## Risks
- **Complexity**: CSS Grid `grid-template-areas` can be verbose
  - **Mitigation**: Use Tailwind `grid-cols-X grid-rows-Y` + `col-span-X row-span-Y`

## Next
1. Define grid layout structure (6-column grid)
2. Apply responsive col/row spans
3. Add hover transitions
4. Test on mobile/desktop
