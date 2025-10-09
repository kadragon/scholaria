# Research: Command Palette (⌘K)

## Goal
Implement global keyboard-accessible command palette for quick admin actions (Topic/Context creation, search, navigation).

## Scope
- Global `⌘K` / `Ctrl+K` shortcut
- Search + action execution
- Context-aware commands (based on current page)
- Integration with existing Refine navigation

## Related Files/Flows
- `frontend/src/components/ui/command.tsx` - shadcn/ui Command component (cmdk wrapper) **already exists**
- `frontend/src/App.tsx:13-106` - Main app structure with routes
- `frontend/src/components/Sidebar.tsx:6-62` - Navigation menu items
- `frontend/src/pages/topics/list.tsx:25-37` - Topic list actions
- `frontend/src/pages/contexts/list.tsx:31-44` - Context list actions
- `frontend/package.json:17` - `cmdk@1.1.1` **already installed**

## Evidence
1. **Command component ready**: Full shadcn/ui implementation with Dialog, Input, List, Group, Item
2. **Navigation actions**: `useNavigation()` hook provides `create()`, `edit()`, `show()` from Refine
3. **Existing routes**:
   - Topics: `/admin/topics`, `/admin/topics/create`, `/admin/topics/edit/:id`
   - Contexts: `/admin/contexts`, `/admin/contexts/create`, `/admin/contexts/edit/:id`, `/admin/contexts/show/:id`
   - Analytics: `/admin/analytics`
   - Chat: `/chat`

## Hypotheses
1. **Global listener**: Use `useEffect` in `App.tsx` or separate hook for `⌘K` detection
2. **Command groups**:
   - **Navigation**: Go to Topics, Contexts, Analytics, Chat
   - **Actions**: Create Topic, Create Context
   - **Search**: Search Topics, Search Contexts (needs data fetching)
3. **Icon support**: Use `lucide-react` (already in deps) for visual hierarchy

## Assumptions/Open Qs
- **Q**: Should we implement full search (fuzzy matching on Topics/Contexts data)?
  - **A**: Start with **navigation + create actions** only (no search). Can add search in phase 2.
- **Q**: Should commands be context-aware (hide/show based on current route)?
  - **A**: Start with **global commands** visible everywhere.

## Risks
- **Keyboard shortcut conflicts**: `⌘K` may conflict with browser search (Safari) → use `event.preventDefault()`
- **Mobile UX**: No keyboard on mobile → ensure command palette is also accessible via button (e.g., in Sidebar)

## Next
1. Create `useCommandPalette` hook for keyboard listener + open state
2. Create `CommandPalette` component with command groups
3. Integrate into `App.tsx` layout
4. Write minimal interaction tests
