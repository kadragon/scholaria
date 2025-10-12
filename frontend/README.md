# Scholaria Admin Frontend

Refine-based admin panel for Scholaria RAG system.

## Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Admin Framework**: Refine v4
- **Router**: React Router v6
- **Data Provider**: REST (FastAPI backend)
- **Auth**: JWT (Bearer token)

## Prerequisites

- Node.js 18+
- FastAPI backend running on `http://localhost:8001`
- Admin user credentials

## Development

```bash
# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start dev server
npm run dev

# Open browser
http://localhost:5173
```

## Build

```bash
npm run build
# Output: dist/
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8001/api` | FastAPI backend URL |
| `E2E_ADMIN_USERNAME` | `admin` | E2E test admin username |
| `E2E_ADMIN_EMAIL` | `admin@scholaria.test` | E2E test admin email |
| `E2E_ADMIN_PASSWORD` | `admin123!@#` | E2E test admin password |

## Project Structure

```
frontend/
├── src/
│   ├── pages/
│   │   ├── topics/       # Topics CRUD
│   │   ├── contexts/     # Contexts CRUD (type-specific forms)
│   │   ├── chat/         # Q&A chat interface
│   │   ├── analytics.tsx # System metrics dashboard
│   │   ├── setup.tsx     # Initial setup wizard
│   │   └── login.tsx     # Login page
│   ├── components/
│   │   ├── ui/           # shadcn/ui components (22)
│   │   ├── CommandPalette.tsx
│   │   ├── InlineEditCell.tsx
│   │   └── Sidebar.tsx
│   ├── providers/
│   │   ├── authProvider.ts    # JWT auth
│   │   └── dataProvider.ts    # REST API client
│   ├── hooks/            # Custom hooks (useChat, useCommandPalette)
│   ├── lib/              # Utilities (apiClient, utils)
│   ├── App.tsx           # Refine setup + routes
│   └── main.tsx
├── .env.example
└── package.json
```

## Features

### Implemented
- ✅ JWT authentication (login/logout)
- ✅ Topics CRUD (List/Create/Edit/Show) with slug-based URLs
- ✅ Contexts CRUD with type-specific forms (Markdown/PDF/FAQ/WebScraper)
- ✅ File upload for PDF contexts (max 100MB)
- ✅ Processing status polling for async operations
- ✅ shadcn/ui integration (22 components: button, dialog, form, table, toast, etc.)
- ✅ Chat interface with topic selector and streaming responses
- ✅ Analytics dashboard with system metrics
- ✅ Setup wizard for initial configuration
- ✅ Command palette (keyboard shortcuts)
- ✅ Inline editing for table cells
- ✅ Responsive layout with sidebar navigation
- ✅ Production build

### TODO
- [ ] Users management (admin user CRUD)
- [ ] Bulk operations UI (multi-select for contexts/topics)

## Testing

### Unit & Integration Tests

```bash
# Run tests
npm test

# Watch mode
npm run test:watch

# Coverage report
npm run test:coverage
```

**Current Coverage**: 62.17% (127 tests)
- Unit tests: dataProvider, authProvider, hooks (useChat, useCommandPalette)
- Integration tests: pages (Login, Setup, Topics, Contexts, Chat)

### E2E Tests (Playwright)

```bash
# Run E2E tests
npm run test:e2e

# UI mode (recommended)
npm run test:e2e:ui

# Debug mode
npm run test:e2e:debug
```

**Test Results**: 28/29 tests passing (96.5% pass rate)
**Test Coverage**:
- ✅ Authentication & Setup flow (6/6)
- ✅ Topic management (CRUD) (7/7)
- ✅ Context ingestion (PDF, Markdown) (6/7)
- ✅ Chat Q&A with streaming responses (6/7) - Multiple messages test failing due to backend session handling
- ✅ Analytics dashboard (5/5)

**Recent Updates**:
- Fixed send button disable issues in chat multi-message scenarios by updating MessageInput component to use DOM-based value validation
- Resolved Redis/Celery configuration issues for backend context processing
- Improved UI locators and API endpoint consistency

See `e2e/README.md` for detailed E2E testing guide.

### Manual Testing

1. Start FastAPI backend (`uv run uvicorn backend.main:app --reload --port 8001`)
2. Start frontend (`npm run dev`)
3. Login with admin credentials (email/password)
4. Test CRUD operations (Topics/Contexts)
5. Test Chat interface with sample topics
6. Verify API calls in Network tab

## Known Issues

- Refine v5 has breaking changes; this project uses v4 for React 18 compatibility
- No TypeScript strict mode (Refine types have some any usage)

## License

Same as main Scholaria project.
