# Plan: Refine Admin Panel Implementation

## Objective
Implement Refine-based admin panel to replace Django Admin, enabling Django removal in Phase 8.

## Constraints
- **TDD**: All FastAPI endpoints have tests before implementation
- **UX Parity**: Match Django Admin feature set (CRUD, bulk ops, file upload)
- **Performance**: <2s page load, <500ms API response p95
- **Browser Support**: Chrome/Firefox/Safari latest 2 versions

## Target Files & Changes

### Step 6.1: FastAPI Admin API Completion (Estimated: 2-3 days)

#### New Endpoints
**File**: `api/routers/admin/bulk_operations.py` (new)
```python
# POST /admin/bulk/assign-context-to-topic
# POST /admin/bulk/regenerate-embeddings
# POST /admin/bulk/update-system-prompt
# POST /admin/bulk/update-processing-status
```

**File**: `api/schemas/admin.py` (extend)
```python
class BulkAssignContextRequest(BaseModel):
    context_ids: list[int]
    topic_id: int

class BulkRegenerateEmbeddingsRequest(BaseModel):
    context_ids: list[int]

class BulkUpdateSystemPromptRequest(BaseModel):
    topic_ids: list[int]
    system_prompt: str
```

**File**: `api/tests/admin/test_bulk_operations.py` (new)
- Test bulk assign (5 contexts → 1 topic)
- Test bulk regenerate embeddings (trigger Celery task)
- Test bulk update system prompt (3 topics)
- Test validation errors (empty IDs, non-existent IDs)

#### Processing Status Endpoint
**File**: `api/routers/admin/contexts.py` (extend)
```python
# GET /admin/contexts/{id}/processing-status
# Returns: { status: "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED", progress: 0-100 }
```

**File**: `api/tests/admin/test_contexts.py` (extend)
- Test polling processing status during upload
- Test status transitions (PENDING → PROCESSING → COMPLETED)

### Step 6.2: Refine Admin Panel (Estimated: 5-7 days)

#### Project Setup
**Directory**: `admin-frontend/` (new)
```bash
npm create refine-app@latest admin-frontend
# Choices:
# - Vite + TypeScript
# - React Router v7
# - REST Data Provider
# - No UI framework (we'll add shadcn/ui manually)
```

**File**: `admin-frontend/package.json` (generated)
```json
{
  "dependencies": {
    "@refinedev/core": "^4.0.0",
    "@refinedev/react-router-v7": "^4.0.0",
    "@refinedev/simple-rest": "^4.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "typescript": "^5.0.0"
  }
}
```

#### shadcn/ui Integration
**File**: `admin-frontend/components.json` (shadcn config)
```bash
npx shadcn-ui@latest init
# Install components: button, input, table, form, dialog, select, toast
npx shadcn-ui@latest add button input table form dialog select toast
```

#### Refine Configuration
**File**: `admin-frontend/src/App.tsx`
```typescript
import { Refine } from "@refinedev/core";
import dataProvider from "@refinedev/simple-rest";
import routerBindings from "@refinedev/react-router-v7";
import { authProvider } from "./providers/authProvider";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001/api/admin";

function App() {
  return (
    <Refine
      dataProvider={dataProvider(API_URL)}
      authProvider={authProvider}
      routerProvider={routerBindings}
      resources={[
        { name: "topics", list: "/topics", create: "/topics/create", edit: "/topics/edit/:id" },
        { name: "contexts", list: "/contexts", create: "/contexts/create", edit: "/contexts/edit/:id" },
        { name: "users", list: "/users" },
      ]}
    />
  );
}
```

**File**: `admin-frontend/src/providers/authProvider.ts`
```typescript
import { AuthProvider } from "@refinedev/core";

export const authProvider: AuthProvider = {
  login: async ({ email, password }) => {
    const res = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const { access_token } = await res.json();
    localStorage.setItem("token", access_token);
    return { success: true };
  },
  logout: async () => {
    localStorage.removeItem("token");
    return { success: true };
  },
  check: async () => {
    const token = localStorage.getItem("token");
    return { authenticated: !!token };
  },
  getIdentity: async () => {
    const token = localStorage.getItem("token");
    const res = await fetch(`${API_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return await res.json();
  },
};
```

#### Resource Pages: Topics
**File**: `admin-frontend/src/pages/topics/list.tsx`
```typescript
import { useTable } from "@refinedev/core";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";

export const TopicList = () => {
  const { tableQueryResult, current, setCurrent, pageSize } = useTable();
  const { data, isLoading } = tableQueryResult;

  return (
    <div>
      <h1>Topics</h1>
      <Button onClick={() => navigate("/topics/create")}>Create Topic</Button>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>System Prompt</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data?.data.map((topic) => (
            <TableRow key={topic.id}>
              <TableCell>{topic.name}</TableCell>
              <TableCell>{topic.system_prompt?.substring(0, 50)}...</TableCell>
              <TableCell>
                <Button onClick={() => navigate(`/topics/edit/${topic.id}`)}>Edit</Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};
```

**File**: `admin-frontend/src/pages/topics/create.tsx`
```typescript
import { useForm } from "@refinedev/react-hook-form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

export const TopicCreate = () => {
  const { refineCore: { onFinish }, handleSubmit, register } = useForm();

  return (
    <form onSubmit={handleSubmit(onFinish)}>
      <Input {...register("name")} placeholder="Topic Name" />
      <Textarea {...register("system_prompt")} placeholder="System Prompt" />
      <Button type="submit">Create</Button>
    </form>
  );
};
```

#### Resource Pages: Contexts (Type-specific)
**File**: `admin-frontend/src/pages/contexts/create.tsx`
```typescript
import { useState } from "react";
import { useForm } from "@refinedev/react-hook-form";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";

export const ContextCreate = () => {
  const [contextType, setContextType] = useState<"PDF" | "MARKDOWN" | "FAQ">("PDF");
  const { refineCore: { onFinish }, handleSubmit, register } = useForm();

  return (
    <form onSubmit={handleSubmit((data) => {
      const formData = new FormData();
      formData.append("name", data.name);
      formData.append("context_type", contextType);
      if (contextType === "PDF" && data.file?.[0]) {
        formData.append("file", data.file[0]);
      }
      onFinish(formData);
    })}>
      <Select value={contextType} onValueChange={setContextType}>
        <SelectTrigger><SelectValue /></SelectTrigger>
        <SelectContent>
          <SelectItem value="PDF">PDF Upload</SelectItem>
          <SelectItem value="MARKDOWN">Markdown</SelectItem>
          <SelectItem value="FAQ">FAQ Q&A</SelectItem>
        </SelectContent>
      </Select>

      {contextType === "PDF" && (
        <input type="file" {...register("file")} accept=".pdf" />
      )}
      {contextType === "MARKDOWN" && (
        <textarea {...register("content")} placeholder="Markdown content" />
      )}
      {contextType === "FAQ" && (
        <div>
          {/* Dynamic Q&A pairs - use useFieldArray */}
        </div>
      )}

      <Button type="submit">Create Context</Button>
    </form>
  );
};
```

#### Bulk Operations
**File**: `admin-frontend/src/pages/contexts/list.tsx`
```typescript
import { useTable, useCustomMutation } from "@refinedev/core";

export const ContextList = () => {
  const { tableQueryResult, selectedRowKeys, setSelectedRowKeys } = useTable({ initialPageSize: 20 });
  const { mutate: bulkAssign } = useCustomMutation();

  const handleBulkAssign = (topicId: number) => {
    bulkAssign({
      url: "/bulk/assign-context-to-topic",
      method: "post",
      values: { context_ids: selectedRowKeys, topic_id: topicId },
    });
  };

  return (
    <div>
      <Button onClick={() => handleBulkAssign(1)}>Assign to Topic 1</Button>
      {/* Table with row selection */}
    </div>
  );
};
```

### Step 6.3: Docker & Nginx Integration (Estimated: 1-2 days)

#### Docker Configuration
**File**: `Dockerfile.admin` (new)
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY admin-frontend/package*.json ./
RUN npm ci
COPY admin-frontend/ ./
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx/admin.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

**File**: `docker-compose.yml` (extend)
```yaml
services:
  admin-frontend:
    build:
      context: .
      dockerfile: Dockerfile.admin
    ports:
      - "3000:80"
    environment:
      VITE_API_URL: http://fastapi:8001/api/admin
```

#### Nginx Configuration
**File**: `nginx/admin.conf`
```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    # Refine SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to FastAPI
    location /api/ {
        proxy_pass http://fastapi:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Test/Validation Cases

### Step 6.1 Tests (api/tests/admin/)
- [ ] `test_bulk_operations.py`:
  - Test bulk assign 5 contexts to topic
  - Test bulk regenerate embeddings triggers Celery tasks
  - Test bulk update system prompt (3 topics)
  - Test validation: empty IDs, non-existent IDs
- [ ] `test_contexts.py`:
  - Test processing status polling (PENDING → COMPLETED)
  - Test upload progress tracking

### Step 6.2 Tests (admin-frontend/)
- [ ] Unit tests (Vitest):
  - Test TopicList renders data from API
  - Test TopicCreate submits form correctly
  - Test ContextCreate switches UI based on type
- [ ] E2E tests (Playwright):
  - Test login → topic list → create topic → edit topic → delete topic
  - Test PDF upload → processing status poll → context created
  - Test bulk assign: select 3 contexts → assign to topic → verify in topic detail

### Step 6.3 Tests
- [ ] Docker integration:
  - `docker compose up -d` → verify admin-frontend accessible at http://localhost:3000
  - Verify API calls routed to FastAPI correctly
  - Test production build with `npm run build`

## Steps (RPI Workflow)

### Step 1: Complete FastAPI Admin API (2-3 days)
1. [ ] Create `api/routers/admin/bulk_operations.py` with TDD
2. [ ] Write tests in `api/tests/admin/test_bulk_operations.py` (Red)
3. [ ] Implement bulk assign, regenerate, update prompt endpoints (Green)
4. [ ] Refactor for code reuse (Refactor)
5. [ ] Add processing status endpoint in `contexts.py`
6. [ ] Test with Swagger UI `/docs`

### Step 2: Refine Project Setup (1 day)
1. [ ] Run `npm create refine-app@latest admin-frontend`
2. [ ] Install shadcn/ui: `npx shadcn-ui@latest init`
3. [ ] Configure authProvider with JWT
4. [ ] Test login flow with FastAPI `/auth/login`

### Step 3: Topics Resource (POC) (1-2 days)
1. [ ] Implement TopicList, TopicCreate, TopicEdit
2. [ ] Test CRUD operations against FastAPI
3. [ ] Validate UX with admin user (1-2 testers)
4. [ ] Iterate based on feedback

### Step 4: Contexts Resource (2-3 days)
1. [ ] Implement type-specific creation forms (PDF/FAQ/Markdown)
2. [ ] Add file upload with progress tracking
3. [ ] Add processing status polling
4. [ ] Implement bulk operations UI

### Step 5: Docker & Nginx (1-2 days)
1. [ ] Create `Dockerfile.admin` multi-stage build
2. [ ] Update `docker-compose.yml` with admin-frontend service
3. [ ] Configure Nginx routing (`/admin` → SPA, `/api` → FastAPI)
4. [ ] Test production build

### Step 6: E2E Testing & Documentation (1 day)
1. [ ] Write Playwright E2E tests
2. [ ] Update `docs/ADMIN_GUIDE.md` with Refine UI instructions
3. [ ] Create video walkthrough for admin users

## Rollback Plan

### Step 6.1 Rollback
- FastAPI endpoints independent; can be disabled without affecting existing functionality
- Django Admin still operational on port 8000

### Step 6.2 Rollback
- Refine frontend separate service; can be stopped without affecting FastAPI
- Django Admin remains fallback

### Step 6.3 Rollback
- Remove `admin-frontend` service from `docker-compose.yml`
- Revert Nginx config to Django-only routing

## Review Hotspots

### Critical Path
1. **File Upload**: Most complex due to FormData handling and progress tracking
2. **Authentication**: JWT refresh logic must be solid to avoid login loops
3. **Bulk Operations**: Row selection state management and mutation coordination

### Performance Targets
- Page load: <2s (Vite build optimized)
- API response: <500ms p95 (already validated in FastAPI tests)
- File upload: <10s for 10MB PDF (network-dependent)

### UX Validation
- Test with 2+ admin users before declaring Step 6.2 complete
- Capture feedback on:
  - CRUD workflow clarity
  - File upload experience
  - Bulk operation discoverability

## Status

- [ ] Step 6.1: FastAPI Admin API Completion
- [ ] Step 6.2: Refine Admin Panel
- [ ] Step 6.3: Docker & Nginx Integration

Next: Implement Step 6.1 with TDD (bulk operations endpoints).
