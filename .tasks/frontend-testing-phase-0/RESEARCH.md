# Research: Frontend Testing Phase 0

## Goal
TASKS.md "Phase 0 – 테스트 인프라 도입" 항목 검증 및 완료 상태 확인

## Scope
- Vitest + React Testing Library + MSW 설치 여부 확인
- `package.json` 스크립트 (`test`, `test:watch`, `coverage`) 확인
- `setupTests.ts` 존재 및 설정 확인
- GitHub Actions 워크플로 프런트엔드 테스트 잡 확인

## Related Files & Flows

### 설치 상태 (package.json)
- **Vitest**: `vitest@^2.1.9` ✅
- **React Testing Library**: `@testing-library/react@^16.3.0` ✅
- **jest-dom**: `@testing-library/jest-dom@^6.9.1` ✅
- **user-event**: `@testing-library/user-event@^14.6.1` ✅
- **MSW**: `msw@^2.11.4` ✅
- **Coverage**: `@vitest/coverage-v8@^2.1.9`, `@vitest/ui@^2.1.9` ✅

### package.json 스크립트
```json
{
  "test": "vitest run",
  "test:watch": "vitest",
  "test:ui": "vitest --ui",
  "test:coverage": "vitest run --coverage"
}
```
✅ 모두 존재

### setupTests.ts
- 위치: `frontend/src/setupTests.ts` ✅
- 내용:
  - `@testing-library/jest-dom` import ✅
  - MSW 서버 (`beforeAll`, `afterEach`, `afterAll`) ✅
  - `cleanup()` 자동 실행 ✅
  - `localStorage`, `sessionStorage` 초기화 ✅

### vitest.config.ts
- `jsdom` 환경 설정 ✅
- `setupFiles: ["./src/setupTests.ts"]` ✅
- Coverage 설정 (provider: v8, reporters: text/json/html) ✅
- Alias `@` → `./src` ✅

### 기존 테스트 파일
- 5개 테스트 파일 존재:
  1. `src/lib/__tests__/apiClient.test.ts` (5 tests)
  2. `src/providers/__tests__/authProvider.test.tsx` (11 tests)
  3. `src/providers/__tests__/ThemeProvider.test.tsx` (7 tests)
  4. `src/components/__tests__/ThemeToggle.test.tsx` (6 tests)
  5. `src/pages/chat/hooks/__tests__/useChat.test.ts` (8 tests)
- **Total: 37 tests passing**

### GitHub Actions
- `.github/workflows/` 디렉토리 **존재하지 않음** ❌
- CI/CD 파이프라인 미설정

## Hypotheses
- **H1**: Phase 0 요구사항 중 **GitHub Actions 워크플로 제외** 모두 완료
- **H2**: TASKS.md 항목이 최신 상태를 반영하지 못함 (이미 완료된 작업)

## Evidence
1. `package.json:12-15` — 모든 스크립트 존재
2. `package.json:53-77` — 모든 의존성 설치 완료
3. `vitest.config.ts:12-28` — JSDOM 환경 + setupFiles + coverage 설정 완료
4. `src/setupTests.ts:1-15` — MSW 서버 라이프사이클 + 스토리지 초기화 완료
5. Frontend test 실행 결과 — 37/37 tests passing
6. `.github/workflows/` 부재 — CI 잡 미설정

## Assumptions/Open Qs
- **A1**: GitHub Actions 워크플로만 추가하면 Phase 0 완료
- **Q1**: 기존 프로젝트에 CI/CD가 없는 이유? (의도적 생략? 추후 계획?)

## Risks
- CI/CD 없이 main 브랜치 보호 불가능 (BRANCH POLICY 위반)
- PR 머지 전 자동 테스트 검증 불가

## Next
- **Plan**: GitHub Actions 워크플로 추가 (frontend test, lint, typecheck 잡)
- Phase 0 완료 후 TASKS.md 업데이트
