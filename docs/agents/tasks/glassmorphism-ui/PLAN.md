# Plan: Glassmorphism UI

## Objective
Apply glassmorphism (frosted glass) effects to Sidebar and modals.

## Constraints
- Subtle effect (avoid excessive blur)
- Maintain readability
- Fallback for older browsers
- Use Tailwind utilities only

## Target Files & Changes

### 1. **Edit: `frontend/src/components/Sidebar.tsx`**
- Change `bg-white` to `bg-white/90`
- Add `backdrop-blur-xl`
- Add `border-r-white/20` for subtle edge
- Adjust shadow for depth

### 2. **Edit: `frontend/src/components/ui/dialog.tsx`**
- Update `DialogContent` overlay background
- Add `backdrop-blur-md` to overlay
- Keep existing animation

## Test/Validation Cases
1. **Sidebar**: Semi-transparent with blur visible behind
2. **Modals**: Frosted overlay effect
3. **Readability**: Text remains clear
4. **Fallback**: Solid background on unsupported browsers

## Steps
1. [ ] Apply glassmorphism to Sidebar
2. [ ] Apply to Dialog overlay
3. [ ] Test visual consistency across pages
4. [ ] Run `npm run typecheck` + `npm run lint`

## Rollback
- Revert Sidebar + Dialog to solid backgrounds

## Review Hotspots
- **Readability**: Ensure text contrast is sufficient
- **Performance**: Check for rendering lag on low-end devices (acceptable trade-off)

## Status
- [ ] Step 1: Sidebar glassmorphism
- [ ] Step 2: Dialog glassmorphism
- [ ] Step 3: Visual testing
- [ ] Step 4: Quality checks
