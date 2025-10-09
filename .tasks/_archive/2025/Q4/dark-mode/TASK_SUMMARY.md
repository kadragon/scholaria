# Task Summary: Dark Mode

## Goal
프런트엔드에 다크 모드 토글 UI와 사용자 선호 저장 기능 추가

## Key Changes
- **ThemeProvider**: CSS 변수 기반 테마 컨텍스트, localStorage 저장, system 감지, `.dark` 클래스 제어
- **ThemeToggle**: light → dark → system 순환 버튼, 아이콘(☀️/🌙/🖥️), 접근성 레이블
- **CSS Variables**: `:root`, `.dark` 스코프에 primary/secondary/accent 50~900 팔레트 정의
- **Tailwind Config**: `darkMode: 'class'`, `hsl(var(--*))` 동적 색상 참조
- **FOUC Prevention**: `index.html` inline script로 localStorage 선제 적용

## Tests
- 13개 신규 테스트 (ThemeProvider: 7, ThemeToggle: 6)
- 37개 전체 통과, typecheck/lint 클린

## Commits
- `d42296f` — [Behavioral] feat: Add dark mode with theme toggle and persistence [dark-mode]
- `ee39050` — [Structural] (dark-mode) Address PR review feedback
- `2fc1314` — Merge pull request #50 (feat/dark-mode)

## Files Modified
- frontend/src/providers/ThemeProvider.tsx
- frontend/src/components/ThemeToggle.tsx
- frontend/src/contexts/ThemeContext.ts
- frontend/src/hooks/useTheme.ts
- frontend/src/App.tsx
- frontend/src/index.css
- frontend/tailwind.config.js
- frontend/index.html
- frontend/src/providers/__tests__/ThemeProvider.test.tsx
- frontend/src/components/__tests__/ThemeToggle.test.tsx
