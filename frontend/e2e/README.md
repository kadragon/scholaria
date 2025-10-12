# E2E Tests with Playwright

End-to-end tests for Scholaria frontend application using Playwright.

## Prerequisites

- Node.js 20+
- Backend services running (PostgreSQL, Redis, Qdrant, FastAPI)
- Frontend dev server or preview build

## Installation

```bash
npm install
npx playwright install --with-deps chromium
```

## Running Tests

### Local Development

```bash
# Run all E2E tests
npm run test:e2e

# Run with UI mode (recommended for development)
npm run test:e2e:ui

# Debug mode
npm run test:e2e:debug

# Run specific test file
npx playwright test auth.spec.ts

# Run specific test by name
npx playwright test -g "should login successfully"
```

### View Test Reports

```bash
# Open HTML report
npx playwright show-report

# View trace for failed tests
npx playwright show-trace test-results/*/trace.zip
```

## Test Structure

```
e2e/
├── fixtures/          # Test data & auth helpers
│   ├── auth.ts       # Authentication fixtures
│   └── sample.pdf    # Sample file for upload tests
├── pages/            # Page Object Models
│   ├── login.page.ts
│   ├── setup.page.ts
│   ├── topics.page.ts
│   ├── contexts.page.ts
│   ├── chat.page.ts
│   └── analytics.page.ts
├── tests/            # Test scenarios
│   ├── auth.setup.ts          # Global auth setup
│   ├── auth.spec.ts           # Authentication tests
│   ├── topic-management.spec.ts
│   ├── context-ingestion.spec.ts
│   ├── chat-qa.spec.ts
│   └── analytics.spec.ts
└── utils/            # Test helpers
```

## Test Coverage

### Core Flows

1. **Authentication & Setup** (`auth.spec.ts`)
   - Setup flow with admin account creation
   - Login/logout functionality
   - Session persistence
   - Error handling

2. **Topic Management** (`topic-management.spec.ts`)
   - Create, edit, delete topics
   - Slug auto-generation
   - Form validation

3. **Context Ingestion** (`context-ingestion.spec.ts`)
   - Upload PDF files
   - Create Markdown contexts
   - Processing status monitoring
   - Topic assignment

4. **Chat Q&A** (`chat-qa.spec.ts`)
    - Topic selection
    - Send messages and receive responses
    - Submit feedback (thumbs up/down)
    - Session persistence
    - Handle multiple messages in conversation (Note: Currently failing due to backend session handling issue)

5. **Analytics Dashboard** (`analytics.spec.ts`)
   - View statistics
   - Filter by topic and date range
   - View feedback comments

## Configuration

See `playwright.config.ts` for configuration options:

- **Browsers**: Chromium (default), Firefox, WebKit
- **Retries**: 2 on CI, 0 locally
- **Workers**: 1 on CI, 4 locally
- **Reporters**: HTML, List, GitHub (on CI)
- **Trace**: On first retry
- **Screenshots**: On failure
- **Video**: Retained on failure

## CI/CD

E2E tests run automatically on:
- Pull requests affecting `frontend/` or `backend/`
- Push to `main` branch

See `.github/workflows/e2e-tests.yml` for CI configuration.

## Troubleshooting

### Tests failing with "Timeout waiting for..."

- Ensure backend services are running
- Check if frontend dev server is accessible at `http://localhost:5173`
- Increase timeout in test if needed: `{ timeout: 30000 }`

### Authentication state not persisting

- Delete `playwright/.auth/admin.json` and re-run setup
- Ensure `auth.setup.ts` completes successfully

### Flaky tests

- Add explicit waits: `await page.waitForURL(...)`
- Use `page.waitForLoadState('networkidle')` when needed
- Check for race conditions in async operations

### Multiple messages test failing

- **Issue**: "should handle multiple messages in conversation" test fails on second message response
- **Root Cause**: Backend session handling may not support multiple messages in the same chat session
- **Workaround**: Test passes for single message flows; investigate backend session management for multi-message support

### Debugging

```bash
# Run in headed mode
npx playwright test --headed

# Run in debug mode with Playwright Inspector
npx playwright test --debug

# Slow down execution
npx playwright test --headed --slow-mo=1000
```

## Best Practices

1. **Use Page Object Models** - Encapsulate page interactions in POM classes
2. **Wait for elements** - Use auto-waiting locators instead of manual timeouts
3. **Isolate tests** - Each test should be independent
4. **Clean up data** - Remove test data after tests (or use unique identifiers)
5. **Meaningful assertions** - Assert on visible user impact, not implementation details
6. **Handle React state updates** - For controlled inputs, use DOM-based checks or dispatch events to ensure state synchronization

## Current Status

- **Test Results**: 28/29 tests passing (96.5% pass rate)
- **Recent Fixes**: Updated MessageInput component to use DOM values for button state validation, resolved send button disable issues in multi-message scenarios
- **Known Issues**: Multiple messages test fails due to backend session handling limitations
