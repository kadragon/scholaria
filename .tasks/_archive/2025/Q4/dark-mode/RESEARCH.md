# Research: Dark Mode Implementation

## Goal
Implement theme toggle functionality with user preference persistence for the Scholaria frontend.

## Scope
- Analyze current styling infrastructure
- Determine best approach for dark mode (CSS variables vs Tailwind classes)
- Identify storage mechanism for user preference
- Locate toggle UI placement

## Related Files & Flows

### Current Styling Stack
- **Tailwind CSS**: Main styling framework
- **shadcn/ui**: Component library with cssVariables enabled (`components.json:9`)
- **No existing theme system**: No `next-themes`, no dark mode variants in use
- **Hard-coded colors**: `tailwind.config.js` defines static color palettes (primary, secondary, accent)
- **Layout structure**: `App.tsx:25-35` Layout component with Sidebar

### Component Files
- `frontend/src/index.css`: Tailwind directives only, no CSS variables defined
- `frontend/tailwind.config.js`: Color tokens without dark mode support
- `frontend/src/components/Sidebar.tsx`: Admin panel navigation (potential toggle location)
- `frontend/src/components/ui/*`: 22 shadcn components using hard-coded color classes

### Storage & State
- **No existing theme provider**: No context/provider for theme state
- **localStorage usage**: `authProvider.ts` uses localStorage for tokens → same pattern for theme preference

## Hypotheses

### H1: CSS Variables Approach (shadcn standard)
**Pros:**
- shadcn components are designed for CSS variable theming
- Single source of truth in `:root` and `.dark` selectors
- No component refactoring needed
- Smooth transitions between themes

**Cons:**
- Requires updating `index.css` with extensive CSS variables
- All Tailwind config colors need variable mapping

### H2: Tailwind dark: Classes
**Pros:**
- Native Tailwind approach
- Fine-grained per-element control

**Cons:**
- Requires updating ~22 UI components + pages with `dark:*` classes
- More maintenance overhead

## Evidence

1. **shadcn cssVariables=true** (`components.json:10`):
   - Indicates project intended to use CSS variable approach
   - Current implementation incomplete (no variables in `index.css`)

2. **Hard-coded color usage patterns**:
   - `button.tsx:14`: `bg-primary-600 text-white`
   - `Sidebar.tsx:31`: `bg-white/90 backdrop-blur-xl`
   - All components use explicit color tokens

3. **No theme toggle in UI**: Sidebar component has placeholder button (line 36) for "빠른 명령" but no theme control

## Assumptions & Open Questions

### Assumptions
- Users expect system preference detection (prefers-color-scheme)
- Theme should persist across sessions
- Toggle should be accessible from any authenticated page
- Chat page (public) also needs theme support

### Open Questions
1. **Toggle placement**: Sidebar (admin only) vs. global header/footer?
   - **Decision needed**: Should public chat page have theme toggle?
2. **Default theme**: Light vs. System preference?
3. **Transition animations**: Instant vs. fade?

## Risks

1. **CSS Variable Scope**: Extensive refactoring of color tokens in `tailwind.config.js`
2. **Component Regression**: 22 UI components + 6 page files may have visual regressions
3. **Test Coverage**: New theme provider needs comprehensive tests (system pref detection, localStorage persistence, toggle behavior)
4. **Accessibility**: WCAG contrast requirements for dark theme colors

## Next Steps
→ **Plan**: Define CSS variable schema, theme provider implementation, toggle component design, and test strategy.
