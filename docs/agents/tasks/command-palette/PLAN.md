# Plan: Command Palette (⌘K)

## Objective
Add global keyboard-accessible command palette for quick admin navigation and actions.

## Constraints
- Use existing `cmdk` component (`frontend/src/components/ui/command.tsx`)
- Integrate with Refine `useNavigation()` hooks
- No new dependencies
- Follow existing UI patterns (shadcn/ui + Tailwind)

## Target Files & Changes

### 1. **New: `frontend/src/hooks/useCommandPalette.tsx`**
- Custom hook managing:
  - `open` state
  - Keyboard listener (`⌘K` / `Ctrl+K`)
  - `toggle()`, `setOpen()` methods

### 2. **New: `frontend/src/components/CommandPalette.tsx`**
- Component structure:
  - `CommandDialog` wrapper
  - `CommandInput` (search)
  - `CommandList` with groups:
    - **Navigation** (Topics, Contexts, Analytics, Chat)
    - **Actions** (Create Topic, Create Context)
  - Icons from `lucide-react`
- Props: `open`, `onOpenChange`
- Uses `useNavigation()` for routing

### 3. **Edit: `frontend/src/App.tsx`**
- Import `CommandPalette` + `useCommandPalette`
- Render `<CommandPalette />` at app root level (inside `BrowserRouter`, outside routes)
- Pass hook state to component

### 4. **Optional: `frontend/src/components/Sidebar.tsx`**
- Add "⌘K" hint button (mobile fallback)

## Test/Validation Cases
1. **Keyboard shortcut**: Press `⌘K` → opens palette
2. **Navigation**: Select "Go to Topics" → navigates to `/admin/topics`
3. **Actions**: Select "Create Topic" → navigates to `/admin/topics/create`
4. **Close**: Press `Esc` → closes palette
5. **Search filtering**: Type "topic" → shows only Topic-related commands

## Steps
1. [ ] Create `useCommandPalette` hook
2. [ ] Create `CommandPalette` component with command groups
3. [ ] Integrate into `App.tsx`
4. [ ] Manual test (keyboard + actions)
5. [ ] Add "⌘K" hint to Sidebar (optional)
6. [ ] Run `npm run typecheck` + `npm run lint`

## Rollback
- Remove `CommandPalette.tsx`, `useCommandPalette.tsx`
- Remove import/usage from `App.tsx`

## Review Hotspots
- **Keyboard event handling**: Ensure `preventDefault()` to avoid browser conflicts
- **Navigation integration**: Verify `useNavigation()` from Refine works correctly
- **Icon imports**: Check `lucide-react` usage consistency

## Status
- [ ] Step 1: Hook implementation
- [ ] Step 2: Component implementation
- [ ] Step 3: App integration
- [ ] Step 4: Manual testing
- [ ] Step 5: Sidebar hint (optional)
- [ ] Step 6: Quality checks
