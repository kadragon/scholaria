# Plan: E2E Testing with Playwright

## Objective
프로덕션 준비를 위한 End-to-End 테스트 도입. 핵심 사용자 플로우 검증 및 시각적 회귀 테스트 기반 마련.

## Constraints
- **Coverage 목표**: 현재 unit/integration에서 커버하지 못한 App.tsx, ChatPage, Analytics 중점
- **시나리오 중심**: 실제 사용자 관점의 플로우 검증
- **CI 통합**: GitHub Actions에서 headless 실행
- **유지보수 가능**: Page Object Model 패턴 적용
- **병렬 실행**: 독립적인 테스트 간 병렬 실행 지원

## Context

### Current State
- **Unit/Integration Tests**: 127 tests, 62.17% coverage
- **Uncovered Critical Paths**:
  - App.tsx (122 LOC, 0%) — BrowserRouter routing, auth flow
  - chat/index.tsx (154 LOC, 0%) — Topic selection, SSE streaming, session management
  - analytics.tsx (399 LOC, 0%) — Chart interactions, date filtering, data visualization
- **Test Gap**: 복잡한 사용자 플로우 검증 부재

### Why Playwright?
1. **Modern API**: Async/await, auto-waiting, TypeScript 네이티브 지원
2. **Multi-browser**: Chromium, Firefox, WebKit 동시 테스트
3. **Developer Tools**: Codegen, trace viewer, UI mode
4. **CI-ready**: Docker 이미지, headless 기본 지원
5. **Community**: Microsoft 공식 지원, 활발한 생태계

### Alternative Considered
- **Cypress**: 좋은 DX, 하지만 iframe 제약 및 multi-tab 지원 제한
- **Selenium**: 성숙하지만 느리고 flaky, 유지보수 비용 높음
- **선택**: Playwright (빠른 실행, 안정성, TypeScript 통합)

## Target Files & Changes

### Phase 1: Setup & Infrastructure
**Duration**: ~2-3 hours

#### Step 1: Playwright Installation & Config
- **파일**: `frontend/package.json`, `frontend/playwright.config.ts`
- **작업**:
  1. Install Playwright: `npm install -D @playwright/test`
  2. Initialize config: `npx playwright install`
  3. Create `playwright.config.ts`:
     - Base URL: http://localhost:5173
     - Browsers: chromium (기본), firefox, webkit (선택)
     - Timeouts: 30s
     - Retries: 2 (CI), 0 (로컬)
     - Workers: 4 (병렬 실행)
     - Screenshot: on failure
     - Trace: on first retry
  4. Create `.gitignore` entries:
     - `test-results/`
     - `playwright-report/`
     - `.auth/` (인증 상태 저장)

#### Step 2: Test Structure Setup
- **디렉토리**: `frontend/e2e/`
- **구조**:
  ```
  frontend/
  ├── e2e/
  │   ├── fixtures/       # Custom fixtures, auth helpers
  │   ├── pages/          # Page Object Models
  │   │   ├── login.page.ts
  │   │   ├── topics.page.ts
  │   │   ├── contexts.page.ts
  │   │   ├── chat.page.ts
  │   │   └── analytics.page.ts
  │   ├── tests/          # Test scenarios
  │   │   ├── auth.spec.ts
  │   │   ├── topic-management.spec.ts
  │   │   ├── context-ingestion.spec.ts
  │   │   ├── chat-qa.spec.ts
  │   │   └── analytics.spec.ts
  │   └── utils/          # Test helpers
  │       ├── db-helpers.ts
  │       └── api-helpers.ts
  └── playwright.config.ts
  ```

#### Step 3: Authentication State Management
- **파일**: `frontend/e2e/fixtures/auth.ts`
- **작업**:
  1. Create global setup for admin login
  2. Save auth state to `.auth/admin.json`
  3. Reuse auth state across tests (빠른 실행)
  4. Create `baseTest` fixture with authenticated context

**Validation**: `npx playwright test --list` 실행 시 구조 확인

---

### Phase 2: Core User Flows (3-5 Critical Scenarios)
**Duration**: ~4-6 hours

#### Test 1: Authentication & Setup Flow
- **파일**: `frontend/e2e/tests/auth.spec.ts`
- **시나리오**:
  1. **Setup needed**: `/admin/login` → redirect to `/admin/setup`
     - Fill: username, email, password, confirm password
     - Submit → success toast → redirect to `/admin/login`
  2. **Login**: Enter email/password → submit → redirect to `/admin/topics`
  3. **Session persistence**: Reload page → still authenticated
  4. **Logout**: Click logout → redirect to `/admin/login` → localStorage cleared
- **Assertions**:
  - URL navigation
  - Toast messages
  - localStorage token presence/absence
  - Protected route access denial when unauthenticated

#### Test 2: Topic Management Flow
- **파일**: `frontend/e2e/tests/topic-management.spec.ts`
- **시나리오**:
  1. **Create topic**:
     - Navigate to `/admin/topics/create`
     - Fill: name, slug (optional), description, system_prompt
     - Submit → success toast → redirect to `/admin/topics`
     - Verify topic appears in list
  2. **Edit topic**:
     - Click edit on created topic
     - Update name, system_prompt
     - Submit → success toast → redirect to list
     - Verify updated data in list
  3. **Delete topic**:
     - Click delete → confirmation dialog
     - Confirm → success toast → topic removed from list
- **Assertions**:
  - Table data matches created/updated values
  - Toast messages
  - List updates after operations

#### Test 3: Context Ingestion Flow
- **파일**: `frontend/e2e/tests/context-ingestion.spec.ts`
- **시나리오**:
  1. **Upload PDF**:
     - Navigate to `/admin/contexts/create`
     - Fill name, description
     - Select PDF tab
     - Upload test PDF file (`e2e/fixtures/sample.pdf`)
     - Submit → processing status appears
     - Wait for "COMPLETED" status (polling)
     - Redirect to `/admin/contexts`
     - Verify context in list with status "COMPLETED"
  2. **Create Markdown context**:
     - Fill name, markdown content
     - Submit → immediate success (no polling)
     - Verify in list
  3. **Assign context to topic**:
     - Edit context
     - Select topics from MultiSelect
     - Submit → verify assignment in list
- **Assertions**:
  - File upload success
  - Processing status updates
  - Context-Topic association

#### Test 4: Chat Q&A Flow
- **파일**: `frontend/e2e/tests/chat-qa.spec.ts`
- **시나리오**:
  1. **Select topic & ask question**:
     - Navigate to `/chat`
     - Select topic from TopicSelector
     - Type question in MessageInput
     - Submit → streaming response appears
     - Verify message appears in MessageList
  2. **SSE streaming**:
     - Mock SSE endpoint (or use real backend)
     - Verify incremental message updates
     - Verify final complete message
  3. **Submit feedback**:
     - Click thumbs up/down on message
     - Verify feedback controls state change
     - Optionally add comment
     - Submit → success toast
  4. **Session persistence**:
     - Reload page → session messages still visible
     - Ask new question → appends to history
- **Assertions**:
  - Topic selection updates URL (`/chat/:slug`)
  - Messages render correctly
  - Feedback submission success
  - Session ID persists in sessionStorage

#### Test 5: Analytics Dashboard Flow
- **파일**: `frontend/e2e/tests/analytics.spec.ts`
- **시나리오**:
  1. **View summary stats**:
     - Navigate to `/admin/analytics`
     - Verify 4 stat cards render
     - Verify chart renders (question trends, feedback distribution)
  2. **Filter by date range**:
     - Select start/end date
     - Verify charts update
     - Verify stats update
  3. **Filter by topic**:
     - Select topic from filter
     - Verify topic-specific stats
  4. **View feedback comments**:
     - Navigate to feedback comments tab
     - Verify comments list renders
     - Filter by topic
- **Assertions**:
  - Chart data matches API response
  - Date filtering works
  - Topic filtering works
  - Comments display correctly

**Validation**: `npx playwright test` 실행 → 5개 시나리오 통과

---

### Phase 3: CI Integration & Reporting
**Duration**: ~1-2 hours

#### Step 4: GitHub Actions Workflow
- **파일**: `.github/workflows/e2e-tests.yml`
- **내용**:
  ```yaml
  name: E2E Tests

  on:
    pull_request:
      paths:
        - 'frontend/**'
        - 'backend/**'
        - '.github/workflows/e2e-tests.yml'
    push:
      branches: [main]

  jobs:
    e2e:
      runs-on: ubuntu-latest
      timeout-minutes: 15

      services:
        postgres:
          image: postgres:17
          env:
            POSTGRES_PASSWORD: postgres
          options: >-
            --health-cmd pg_isready
            --health-interval 10s
            --health-timeout 5s
            --health-retries 5
        redis:
          image: redis:7
        qdrant:
          image: qdrant/qdrant:v1.12.5

      steps:
        - uses: actions/checkout@v4

        - name: Setup Python
          uses: actions/setup-python@v5
          with:
            python-version: '3.13'

        - name: Setup Node.js
          uses: actions/setup-node@v4
          with:
            node-version: '22'

        - name: Install backend dependencies
          run: pip install uv && uv sync

        - name: Run migrations
          run: uv run alembic upgrade head

        - name: Start backend
          run: uv run uvicorn backend.main:app --host 0.0.0.0 --port 8001 &

        - name: Install frontend dependencies
          run: cd frontend && npm ci

        - name: Install Playwright browsers
          run: cd frontend && npx playwright install --with-deps chromium

        - name: Build frontend
          run: cd frontend && npm run build

        - name: Start frontend
          run: cd frontend && npm run preview -- --port 5173 &

        - name: Wait for services
          run: |
            npx wait-on http://localhost:8001/health http://localhost:5173 -t 60000

        - name: Run E2E tests
          run: cd frontend && npx playwright test

        - name: Upload test results
          if: always()
          uses: actions/upload-artifact@v4
          with:
            name: playwright-report
            path: frontend/playwright-report/
            retention-days: 7

        - name: Upload trace on failure
          if: failure()
          uses: actions/upload-artifact@v4
          with:
            name: playwright-traces
            path: frontend/test-results/
            retention-days: 7
  ```

#### Step 5: HTML Reporter & Trace Viewer
- **설정**: `playwright.config.ts`
  ```typescript
  reporter: [
    ['html', { open: 'never' }],
    ['list'],
    ['github'], // GitHub Actions annotations
  ]
  ```
- **로컬 개발**:
  - `npx playwright test --ui` (UI mode, 실시간 디버깅)
  - `npx playwright show-report` (HTML 리포트)
  - `npx playwright show-trace test-results/trace.zip` (트레이스 뷰어)

**Validation**: PR에서 E2E 테스트 자동 실행 확인

---

### Phase 4: Visual Regression Testing (Optional)
**Duration**: ~2-3 hours

#### Step 6: Screenshot Comparison
- **파일**: `frontend/e2e/tests/visual.spec.ts`
- **시나리오**:
  1. **Capture baseline screenshots**:
     - Login page
     - Topics list (with data)
     - Chat interface (with messages)
     - Analytics dashboard
  2. **Compare on changes**:
     - Playwright auto-compares screenshots
     - Fail on pixel differences > threshold
- **설정**:
  ```typescript
  await expect(page).toHaveScreenshot('login-page.png', {
    maxDiffPixels: 100,
  });
  ```

#### Step 7: Accessibility Testing (Optional)
- **Tool**: `@axe-core/playwright`
- **통합**:
  ```typescript
  import AxeBuilder from '@axe-core/playwright';

  test('should not have accessibility violations', async ({ page }) => {
    await page.goto('/admin/topics');
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });
  ```

**Validation**: Visual regression 베이스라인 생성 완료

---

## Test/Validation Cases

### Pre-commit
- `npx playwright test` (로컬)
- `npm run lint && npm run typecheck` (프론트엔드)

### CI (PR)
- All E2E tests (headless chromium)
- HTML report 생성
- Trace 저장 (실패 시)

### Release
- All browsers (chromium, firefox, webkit)
- Visual regression tests
- Accessibility tests

## Steps

1. [ ] **Phase 1: Setup & Infrastructure** (~2-3 hours)
   - [ ] Step 1: Playwright installation & config
   - [ ] Step 2: Test structure setup (e2e/, pages/, fixtures/)
   - [ ] Step 3: Authentication state management

2. [ ] **Phase 2: Core User Flows** (~4-6 hours)
   - [ ] Test 1: Authentication & Setup flow
   - [ ] Test 2: Topic Management flow
   - [ ] Test 3: Context Ingestion flow
   - [ ] Test 4: Chat Q&A flow
   - [ ] Test 5: Analytics Dashboard flow

3. [ ] **Phase 3: CI Integration** (~1-2 hours)
   - [ ] Step 4: GitHub Actions workflow
   - [ ] Step 5: HTML reporter & trace viewer

4. [ ] **Phase 4: Visual Regression (Optional)** (~2-3 hours)
   - [ ] Step 6: Screenshot comparison
   - [ ] Step 7: Accessibility testing

5. [ ] **Documentation & Handoff**
   - [ ] Update `frontend/README.md` with E2E test section
   - [ ] Create `frontend/e2e/README.md` with setup/run instructions
   - [ ] Update `.tasks/TASKS.md` with completion status

## Rollback
- Phase 1 실패: `npm uninstall @playwright/test`, config 파일 삭제
- Phase 2 실패: 특정 테스트 스킵 또는 삭제, 핵심 플로우만 유지
- Phase 3 실패: CI workflow 비활성화, 로컬 테스트만 유지
- Phase 4 실패: Visual/a11y 테스트 제외, 기능 테스트만 유지

## Review Hotspots
- **Flaky tests**: SSE streaming, polling logic (재시도 로직 필수)
- **Test data isolation**: 각 테스트 후 DB cleanup 또는 독립적인 데이터 사용
- **Performance**: 병렬 실행 시 DB 경쟁 조건 확인
- **CI timeout**: 15분 제한, 느린 테스트는 별도 job으로 분리

## Dependencies

### NPM Packages (frontend)
- `@playwright/test`: ^1.48.0 (latest stable)
- `@axe-core/playwright`: ^4.10.0 (optional, accessibility)

### Tools
- Playwright browsers (chromium, firefox, webkit)
- wait-on (CI에서 서비스 대기)

### Backend
- 테스트용 DB 셋업 (docker-compose 기반)
- 테스트 데이터 시드 스크립트 (선택)

## Timeline Estimate
- **Phase 1**: 2-3 hours
- **Phase 2**: 4-6 hours
- **Phase 3**: 1-2 hours
- **Phase 4**: 2-3 hours (optional)
- **Total**: **7-11 hours** (핵심만), **9-14 hours** (visual/a11y 포함)

## Success Criteria
1. ✅ 5개 핵심 플로우 E2E 테스트 작성 완료
2. ✅ 모든 테스트 Green (로컬 + CI)
3. ✅ CI에서 자동 실행 (PR, main push)
4. ✅ HTML report 생성 및 trace 저장
5. ✅ Page Object Model 패턴 적용 (유지보수 용이)
6. ✅ 평균 실행 시간 < 5분 (병렬 실행)
7. ✅ Flakiness < 5% (재시도 포함)
8. ✅ 문서화 완료 (README, 실행 가이드)

## Out of Scope
- ❌ **부하 테스트**: E2E 범위 밖, 별도 도구 사용 (k6, Artillery)
- ❌ **보안 테스트**: Penetration testing은 별도 프로세스
- ❌ **크로스 브라우저 전체 커버**: Chromium 우선, Firefox/WebKit 선택적
- ❌ **모바일 테스트**: Desktop 우선, mobile viewport는 선택적

## Next Steps After Completion
1. **Coverage 재평가**: E2E로 간접 커버된 파일 확인 → 전체 커버리지 추정
2. **Threshold 조정**: Unit (62%) + E2E (간접) → 70%+ 예상
3. **Monitoring 통합**: E2E 테스트 실패 시 Sentry/Slack 알림
4. **성능 벤치마크**: E2E 테스트에서 응답 시간 측정 → 회귀 감지
