# Research: Refine Admin Panel Implementation

## Goal
Implement Refine-based admin panel to replace Django Admin, completing Phase 6 of Django→FastAPI migration.

## Scope
- FastAPI Admin API (Step 6.1): Complete CRUD + bulk operations endpoints
- Refine Admin Panel (Step 6.2): React SPA with shadcn/ui
- Docker & Nginx (Step 6.3): Production deployment integration

## Related Files & Flows

### Existing Django Admin Features (to replicate)
- **Topic Management**: `rag/admin.py:TopicAdmin`
  - CRUD operations, multi-select contexts, bulk system prompt updates
- **Context Management**: `rag/admin.py:ContextAdmin`
  - Type-specific creation workflows (PDF/FAQ/Markdown)
  - File upload with real-time processing status
  - Inline Q&A editing (FAQ type)
  - Chunk preview and statistics
- **Bulk Operations**: Custom admin actions
  - Bulk assign to context, move to context, regenerate embeddings
  - Update processing status, context type, system prompt

### FastAPI Admin API Status (Step 6.1)
**Completed**:
- ✅ `api/routers/admin/contexts.py`: Context CRUD with file upload
- ✅ `api/routers/admin/topics.py`: Topic CRUD
- ✅ `api/routers/admin/users.py`: User management
- ✅ `api/schemas/admin.py`: Admin-specific Pydantic schemas
- ✅ `api/dependencies/auth.py`: `require_admin` dependency
- ✅ Tests: 16/16 passing in `api/tests/admin/`

**Missing (to implement in Step 6.1)**:
- [ ] Bulk operations endpoints:
  - POST `/admin/contexts/bulk-assign-topic`
  - POST `/admin/contexts/bulk-regenerate-embeddings`
  - POST `/admin/topics/bulk-update-system-prompt`
- [ ] Real-time processing status (SSE or WebSocket)
- [ ] File upload progress tracking

### Refine Stack Research

**Core Libraries**:
- `@refinedev/core`: Framework core with hooks (useTable, useForm, useShow)
- `@refinedev/react-router-v7`: Routing integration
- `@refinedev/simple-rest`: REST Data Provider
- `@tanstack/react-query`: State management (built-in)

**UI Framework Options**:
1. **shadcn/ui** (recommended)
   - Pros: Tailwind-based, modern, copy-paste components, full control
   - Cons: More manual setup vs pre-built kits
2. **Material-UI**
   - Pros: Pre-built Refine integration (`@refinedev/mui`)
   - Cons: Heavier, opinionated design

**Decision**: shadcn/ui for consistency with modern FastAPI philosophy.

## Hypotheses

1. **H1**: Refine's `useTable` + `useForm` hooks can handle all Django Admin CRUD patterns
2. **H2**: File upload with progress tracking achievable via `useForm` + axios progress events
3. **H3**: Bulk operations implementable via custom mutations + selected row keys
4. **H4**: Real-time processing status via polling (simpler than SSE/WebSocket for MVP)

## Evidence

### H1: CRUD Pattern Coverage
- Refine `useTable`: Sorting, filtering, pagination ✅
- Refine `useForm`: Create/edit with validation ✅
- Refine `useShow`: Detail views with related data ✅
- Django Admin equivalents: `list_display`, `ModelAdmin`, `get_queryset` ✅

### H2: File Upload
- Example from Refine docs: `<input type="file" />` + `FormData` in `onFinish` ✅
- Progress tracking: `axios.request({ onUploadProgress })` ✅
- FastAPI `UploadFile` already implemented in `api/routers/admin/contexts.py` ✅

### H3: Bulk Operations
- Refine `useTable` provides `selectedRowKeys` state ✅
- Custom mutation: `useCustomMutation` hook for bulk endpoints ✅
- Django equivalent: Admin actions (`@admin.action`) ✅

### H4: Processing Status
- Polling: `useQuery` with `refetchInterval` (simple, reliable) ✅
- SSE/WebSocket: More complex, defer to post-MVP optimization ✅

## Assumptions & Open Questions

### Assumptions
1. FastAPI Admin API is feature-complete for initial Refine integration
2. shadcn/ui components sufficient for all Django Admin UI patterns
3. React Query (built-in Refine) handles caching and optimistic updates
4. Nginx can route `/admin` (SPA) and `/api` (FastAPI) correctly

### Open Questions
1. **Q1**: Do we need SSE for real-time processing status in MVP?
   - **Decision**: No, use polling (3-5s interval) for simplicity. Revisit if UX suffers.
2. **Q2**: How to handle Django Admin's inline Q&A editor (FAQ contexts)?
   - **Research**: Use dynamic form fields with `useFieldArray` (react-hook-form compatible).
3. **Q3**: Authentication flow for Refine SPA?
   - **Research**: Refine `authProvider` + JWT stored in `localStorage` + refresh token strategy.

## Sub-agent Findings
(None used for initial research; manual review of Refine docs and FastAPI code sufficient)

## Risks

### High
- **UX Parity**: Refine admin may not match Django Admin's polish out-of-box
  - **Mitigation**: Iterative user testing with admin users (2+ testers)
- **File Upload Reliability**: Large PDFs (>10MB) may timeout or fail
  - **Mitigation**: Chunked upload or presigned URL strategy (post-MVP)

### Medium
- **Learning Curve**: Team unfamiliar with Refine and React Query
  - **Mitigation**: POC with single resource (Topics) before full implementation
- **Authentication Token Expiry**: JWT refresh logic needed
  - **Mitigation**: Implement refresh token endpoint + interceptor

### Low
- **Browser Compatibility**: Modern browsers only (ES2020+)
  - **Acceptable**: School admins use modern browsers

## Next Steps

1. **Complete Step 6.1**: Implement missing bulk operation endpoints
2. **POC Step 6.2**: Create minimal Refine app with Topics resource only
3. **Validate POC**: Admin user testing for CRUD workflows
4. **Full Implementation**: Add Contexts, Users, bulk operations
5. **Docker Integration (Step 6.3)**: Nginx routing + production build
