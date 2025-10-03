# Research: Glassmorphism UI

## Goal
Apply glassmorphism effects to Sidebar and modals for modern aesthetic.

## Scope
- **Sidebar**: Semi-transparent background + backdrop blur
- **Modals**: Dialog components with frosted glass effect
- Subtle borders + shadows for depth

## Related Files/Flows
- `frontend/src/components/Sidebar.tsx:1-62` - Navigation sidebar
- `frontend/src/components/ui/dialog.tsx` - Dialog component (used in modals)
- `frontend/tailwind.config.js` - Tailwind config (may need backdrop-blur utilities)

## Evidence
1. **Current Sidebar**: Solid white background (`bg-white`)
2. **Current modals**: Solid backgrounds in Dialog components
3. **Tailwind support**: `backdrop-blur-*` utilities available by default

## Hypotheses
1. **Glassmorphism formula**:
   - `bg-white/80` or `bg-white/70` (semi-transparent)
   - `backdrop-blur-lg` or `backdrop-blur-xl`
   - `border border-white/20`
   - `shadow-xl`
2. **Apply to**:
   - Sidebar container
   - Dialog overlays (CommandPalette, Context/Topic dialogs)

## Assumptions/Open Qs
- **Q**: Should we add glassmorphism to all cards?
  - **A**: **No** - only Sidebar + modals (avoid overdoing it)
- **Q**: Performance impact of backdrop-blur?
  - **A**: Minimal on modern browsers, acceptable trade-off

## Risks
- **Browser compatibility**: backdrop-blur requires modern browsers
  - **Mitigation**: Provide fallback solid background

## Next
1. Apply glassmorphism to Sidebar
2. Apply to Dialog component (global)
3. Test visual consistency
