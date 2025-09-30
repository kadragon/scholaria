# Django → FastAPI 전환 계획

## Objective
Scholaria RAG 시스템을 Django에서 FastAPI로 점진적으로 전환하며, **관리 인터페이스 손실을 최소화**하고 기존 기능 보존

## Constraints
- **운영 중단 최소화**: 단계별 마이그레이션, 병렬 실행 가능
- **기능 유지**: 381개 테스트 모두 통과, 관리 UI 동등 제공
- **TDD 원칙**: 각 단계 테스트 우선 작성
- **롤백 가능**: 각 단계 독립적으로 복구 가능

## Target Files & Changes

### Phase 1: 기반 구조 준비 (1-2주)
**Goal**: FastAPI 환경 구축, 하이브리드 실행

- [ ] **의존성 추가** (`pyproject.toml`)
  - `fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `fastapi-users`, `pydantic-settings`
- [ ] **FastAPI 앱 초기화** (`api/main.py` 생성)
  - 기본 라우터, CORS, 예외 처리
- [ ] **SQLAlchemy 모델 생성** (`api/models.py`)
  - Topic, Context, ContextItem, QuestionHistory → SQLAlchemy 모델 매핑
- [ ] **Alembic 초기화** (`alembic/`)
  - Django migrations → Alembic 마이그레이션 스크립트 생성
- [ ] **Docker 수정** (`docker-compose.yml`)
  - FastAPI 컨테이너 추가 (포트 8001), Django와 병렬 실행

**Validation**:
- FastAPI 앱 기동 확인 (`/docs` 엔드포인트)
- SQLAlchemy 모델로 DB 읽기 성공
- Django Admin 여전히 동작 (포트 8000)

---

### Phase 2: Read-Only API 전환 (1-2주)
**Goal**: 조회 API만 FastAPI로 이전

- [ ] **API 라우터 생성** (`api/routers/`)
  - [x] topics.py: GET /api/topics, GET /api/topics/{id}
  - [x] contexts.py: GET /api/contexts, GET /api/contexts/{id}
  - [x] history.py: GET /api/history ▶ (slug: fastapi-readonly-api)
- [x] **Pydantic 스키마** (`api/schemas.py`)
  - TopicOut, ContextOut, QuestionHistoryOut
- [ ] **서비스 레이어** (`api/services/`)
  - Django `rag/retrieval/` 로직 복사 → SQLAlchemy 쿼리로 변환
- [ ] **테스트 포팅** (`api/tests/`)
  - `rag/tests/test_views.py` 조회 테스트 → FastAPI TestClient로 재작성

**Validation**:
- 기존 Django API와 동일한 응답 확인 (integration test)
- FastAPI `/api/topics` vs Django `/rag/api/topics` 비교

---

### Phase 3: RAG 엔드포인트 전환 (2-3주)
**Goal**: 핵심 RAG 질의응답 API 이전

- [ ] **RAG 라우터** (`api/routers/rag.py`)
  - POST /api/rag/ask (기존 `AskQuestionView`)
- [ ] **RAG 서비스 통합** (`api/services/rag.py`)
  - `rag/retrieval/rag.py` → FastAPI 의존성 주입 패턴으로 재작성
  - Qdrant, OpenAI 클라이언트 비동기화 (`async def`)
- [ ] **캐싱** (`api/dependencies/cache.py`)
  - Redis 캐싱 전략 (FastAPI-Cache2 또는 커스텀)
- [ ] **Rate Limiting** (`slowapi` 통합)
  - 기존 DRF throttle 동등 기능
- [ ] **테스트**
  - `rag/tests/test_retrieval.py`, `test_e2e_integration.py` 포팅

**Validation**:
- RAG 응답 품질 동등성 확인 (golden dataset 테스트)
- 성능 벤치마크 (Django vs FastAPI 응답 시간)

---

### Phase 4: Write API 전환 (2-3주)
**Goal**: 생성/수정/삭제 API 이전

- [ ] **Write 라우터** (`api/routers/`)
  - POST /api/contexts (Context 생성, 파일 업로드)
  - PUT/DELETE /api/contexts/{id}
  - POST /api/contexts/{id}/qa (FAQ Q&A 추가)
- [ ] **파일 업로드** (`api/services/ingestion.py`)
  - `rag/ingestion/` 로직 → FastAPI `UploadFile` 처리
  - 임시 파일 워크플로우 유지 (PDF 파싱 → 폐기)
- [ ] **Celery 통합** (`api/tasks.py`)
  - FastAPI → Celery 작업 큐잉 (Django와 동일한 Celery 워커 사용)
- [ ] **테스트**
  - `test_ingestion.py`, `test_celery_integration.py` 포팅

**Validation**:
- PDF 업로드 → 청킹 → 임베딩 생성 전체 워크플로우 통과
- Celery 작업 Django/FastAPI 모두 처리 확인

---

### Phase 5: 인증/권한 (1-2주)
**Goal**: 세션 기반 인증 → JWT/OAuth2 전환

- [ ] **FastAPI-Users 통합** (`api/auth/`)
  - 사용자 모델, JWT 토큰 발급
- [ ] **마이그레이션 스크립트**
  - Django 세션 → JWT 토큰 발급 (일회성 마이그레이션)
- [ ] **의존성 가드** (`api/dependencies/auth.py`)
  - `Depends(current_active_user)` 적용
- [ ] **테스트**
  - 인증 플로우 end-to-end 테스트

**Validation**:
- 기존 사용자 로그인 가능
- 보호된 엔드포인트 인증 통과

---

### Phase 6: 관리 인터페이스 (4-6주) ⚠️ Critical
**Goal**: Django Admin → Refine Admin Panel 전환

**결정사항**: Refine + FastAPI Admin API (Option A)
- **이유**:
  - Django 무게감 제거, 헤드리스 아키텍처 (FastAPI와 철학 일치)
  - React Query 내장 → FastAPI 비동기와 완벽한 조합
  - shadcn/ui 또는 Material-UI 선택 가능 (기존 Scholaria는 단순한 UI)
  - 빌트인 Data Provider → REST API 연동 간단
- **리스크**: 개발 기간 길고, 프론트엔드 리소스 필요 (Refine 학습 곡선은 낮음)

#### Step 6.1: FastAPI Admin API (2주)
- [ ] **Admin API 라우터** (`api/routers/admin/`)
  - `topics.py`: CRUD + 대량 작업 (bulk_update_system_prompt)
  - `contexts.py`: CRUD + 파일 업로드 + Context 타입별 워크플로우
  - `users.py`: 사용자 관리 (fastapi-users 기반)
  - `bulk_operations.py`: 대량 할당, 이동, 재생성 임베딩
- [ ] **파일 업로드 엔드포인트** (`/admin/contexts/upload`)
  - PDF 업로드 → 파싱 → 청킹 → 임베딩 생성 (비동기)
  - 처리 상태 스트리밍 (Server-Sent Events 또는 WebSocket)
- [ ] **Pydantic 스키마 확장** (`api/schemas/admin.py`)
  - AdminTopicIn/Out, AdminContextIn/Out (모든 필드 포함)
  - BulkOperationRequest, FileUploadResponse
- [ ] **권한 관리** (`api/dependencies/admin.py`)
  - `Depends(require_admin)` 의존성 가드
  - 역할 기반 접근 제어 (Admin, Editor, Viewer)
- [ ] **테스트** (`api/tests/admin/`)
  - `test_admin_topics.py`, `test_admin_contexts.py`, `test_bulk_operations.py`
  - 기존 `rag/tests/test_admin.py` 시나리오 포팅 (381개 테스트 중 ~50개)

**Validation**:
- Swagger UI (`/docs`)에서 모든 Admin API 동작 확인
- Postman 테스트: PDF 업로드 → Context 생성 → 청크 확인

---

#### Step 6.2: Refine Admin Panel (2-3주)
- [ ] **프로젝트 초기화** (`admin-frontend/`)
  - `npm create refine-app@latest` 실행
  - 선택: Vite + TypeScript + **shadcn/ui** (또는 Material-UI)
  - REST Data Provider 선택
- [ ] **Data Provider 구성** (`src/providers/dataProvider.ts`)
  - Refine REST Data Provider 설정
  - FastAPI Admin API Base URL 연결
  - 인증 헤더 자동 주입 (JWT 토큰)
  ```typescript
  import dataProvider from "@refinedev/simple-rest";

  const API_URL = "http://localhost:8001/api/admin";

  export const adminDataProvider = dataProvider(API_URL, axiosInstance);
  ```
- [ ] **Resource 정의** (`src/App.tsx`)
  - Refine `<Refine>` 컴포넌트에서 resources 정의
  ```typescript
  <Refine
    dataProvider={adminDataProvider}
    authProvider={authProvider}
    resources={[
      {
        name: "topics",
        list: "/topics",
        create: "/topics/create",
        edit: "/topics/edit/:id",
        show: "/topics/show/:id",
      },
      {
        name: "contexts",
        list: "/contexts",
        create: "/contexts/create",
        edit: "/contexts/edit/:id",
        show: "/contexts/show/:id",
      },
      // ... 기타 리소스
    ]}
  />
  ```
- [ ] **Resource 페이지** (`src/pages/`)
  - `topics/`: List, Create, Edit, Show 컴포넌트
    - `useTable` 훅으로 목록 관리 (정렬, 필터, 페이지네이션)
    - `useForm` 훅으로 생성/수정 폼
    - Context 다중 선택 (useSelect 훅 + Select 컴포넌트)
  - `contexts/`: List, Create, Edit, Show 컴포넌트
    - **타입별 생성 폼** (`useForm` + 조건부 렌더링)
      - PDF: 파일 업로드 → 실시간 처리 상태
      - FAQ: 인라인 Q&A 추가 폼
      - Markdown: 텍스트 에디터
    - **청크 미리보기** (Drawer 또는 Modal)
    - **처리 상태 표시** (폴링 또는 Server-Sent Events)
  - `users/`: 사용자 관리 페이지
- [ ] **대량 작업** (Refine `useTable` + `selectedRowKeys`)
  - 테이블에서 여러 행 선택
  - 대량 작업 버튼: 할당, 재생성, 상태 변경
  - FastAPI `/admin/bulk_*` 엔드포인트 호출
- [ ] **파일 업로드**
  - shadcn/ui Input (type="file") 또는 react-dropzone
  - `useForm`에서 파일 처리 (`onFinish` 시 FormData 전송)
  - 진행률: Refine `useCustomMutation` + progress 이벤트
- [ ] **인증** (`src/providers/authProvider.ts`)
  - Refine Auth Provider 구현
  ```typescript
  export const authProvider: AuthProvider = {
    login: async ({ email, password }) => {
      // FastAPI POST /auth/login
      const { token } = await api.post("/auth/login", { email, password });
      localStorage.setItem("token", token);
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
      // FastAPI GET /auth/me
      return await api.get("/auth/me");
    },
  };
  ```
- [ ] **테스트** (`src/__tests__/`)
  - React Testing Library: 주요 폼 동작 테스트
  - E2E (Playwright): 로그인 → Context 생성 → 청크 확인 → 삭제

**Validation**:
- 모든 Django Admin 기능 동등 제공:
  - ✅ Context 타입별 생성 워크플로우 (PDF/FAQ/Markdown)
  - ✅ 파일 업로드 → 실시간 처리 상태
  - ✅ 인라인 Q&A 추가 (FAQ)
  - ✅ 대량 작업 (할당, 이동, 재생성)
  - ✅ 청크 통계 표시 (chunk_count, processing_status)
- 사용성 테스트: Admin 사용자 피드백 (최소 2명)
- Refine Devtools로 데이터 플로우 검증

---

#### Step 6.3: Docker & Nginx 통합 (3-5일)
- [ ] **Docker 구성** (`docker-compose.yml`)
  - `admin-frontend` 서비스 추가 (Vite 빌드 → Nginx 서빙)
  - Production: Multi-stage build (`Dockerfile.admin`)
  ```dockerfile
  # Dockerfile.admin
  FROM node:20-alpine AS builder
  WORKDIR /app
  COPY package*.json ./
  RUN npm ci
  COPY . .
  RUN npm run build

  FROM nginx:alpine
  COPY --from=builder /app/dist /usr/share/nginx/html
  COPY nginx/admin.conf /etc/nginx/conf.d/default.conf
  ```
- [ ] **Nginx 라우팅** (`nginx/nginx.conf`)
  - `/admin` → Refine 정적 파일 (React SPA)
  - `/api` → FastAPI (8001 포트)
  - `/docs` → FastAPI Swagger UI
  - SPA 라우팅 지원 (try_files $uri /index.html)
- [ ] **환경 변수** (`.env.prod`)
  - `VITE_API_BASE_URL=https://your-domain.com/api`
  - `CORS_ALLOWED_ORIGINS=https://your-domain.com`
- [ ] **CORS 설정** (`api/main.py`)
  - Refine Admin Origin 허용
  ```python
  from fastapi.middleware.cors import CORSMiddleware

  app.add_middleware(
      CORSMiddleware,
      allow_origins=["http://localhost:5173", "https://your-domain.com"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

**Validation**:
- Docker Compose 전체 스택 기동 (PostgreSQL, Redis, Qdrant, FastAPI, Refine)
- `https://your-domain.com/admin` → Refine 로그인 → Context 생성 → 청크 확인

---

### Phase 7: 템플릿 → 프론트엔드 분리 (2-3주) (Optional)
**Goal**: Django 템플릿 제거, SPA 전환

- [ ] **React/Vue 앱** (`frontend/`)
  - Topic 선택, Q&A 인터페이스, 질문 히스토리
- [ ] **정적 파일 서빙** (Nginx)
  - FastAPI는 API만, Nginx가 React 빌드 서빙
- [ ] **테스트**
  - `test_landing_page.py`, `test_ui_enhancements.py` E2E 테스트

**Validation**:
- 모든 웹 UI 기능 동작 (모바일 포함)

---

### Phase 8: Django 종료 (1주)
**Goal**: Django 완전 제거

- [ ] **Django 코드 삭제**
  - `core/`, `rag/` (백업 후 제거)
- [ ] **Docker 정리**
  - Django 컨테이너 제거, 포트 8000 → FastAPI
- [ ] **문서 업데이트**
  - README, DEPLOYMENT.md
- [ ] **최종 테스트**
  - 모든 381개 테스트 FastAPI 환경에서 재실행

**Validation**:
- 프로덕션 배포 후 모니터링 (7일)
- 성능 메트릭 비교 (Django vs FastAPI)

---

## Test/Validation Cases

### 각 Phase 공통
- [ ] 기존 테스트 커버리지 유지 (≥95%)
- [ ] 성능 벤치마크 (응답 시간, 메모리)
- [ ] 보안 검사 (OWASP Top 10)

### Critical Path Tests
- [ ] End-to-end RAG workflow (질문 → 답변 → 인용)
- [ ] PDF 업로드 → 청킹 → 임베딩 → 검색
- [ ] 관리자 Context 생성 전체 워크플로우

---

## Rollback

### Phase 1-5
- FastAPI 컨테이너 중지, Django로 트래픽 복귀 (Nginx 설정 변경)
- DB 변경 없음 (SQLAlchemy = Django ORM)

### Phase 6-7
- Django Admin 백업 유지 (병렬 실행)
- 문제 시 Django 8000 포트 재활성화

### Phase 8
- Git 태그 생성 (`v1.0-django`), 롤백 시 재배포
- DB 스냅샷 백업

---

## Review Hotspots

### 주의 필요 영역
1. **ORM 쿼리 변환**: Django Q objects → SQLAlchemy filters
2. **시그널/후크**: Django signals → SQLAlchemy events
3. **파일 업로드**: `request.FILES` → `UploadFile`
4. **캐싱**: Django cache → Redis direct
5. **타임존**: Django `auto_now` → SQLAlchemy `onupdate`

### 성능 검증
- RAG 질의응답 p95 < 3초
- 동시 요청 100 RPS 처리
- 메모리 사용량 < 512MB (FastAPI 컨테이너)

---

## Risks

### High
- **관리 UI 공백**: Phase 6 실패 시 운영 불가 → Option B (하이브리드) 대비
- **ORM 버그**: 복잡한 쿼리 변환 실수 → 철저한 integration test

### Medium
- **팀 학습 곡선**: FastAPI 미숙 → POC로 사전 학습 (1주)
- **성능 미달**: 예상 이점 미미 → Phase 3에서 조기 검증

### Low
- Celery, Qdrant 호환성 (이미 프레임워크 독립적)

---

## Status

### 결정사항 (2025-09-30)
- ✅ **전환 동기**: Django 무거움 → FastAPI 경량화
- ✅ **관리 UI 전략**: Refine Admin Panel (Option A)
- ✅ **React 라이브러리**: Refine (헤드리스, 유연, FastAPI와 철학 일치)
- ✅ **UI 프레임워크**: shadcn/ui (추천) 또는 Material-UI

### 진행 상황
- [ ] Phase 1: 기반 구조 준비 (1-2주)
- [ ] Phase 2: Read-Only API 전환 (1-2주)
- [ ] Phase 3: RAG 엔드포인트 전환 (2-3주)
- [ ] Phase 4: Write API 전환 (2-3주)
- [ ] Phase 5: 인증/권한 (1-2주)
- [ ] Phase 6: 관리 인터페이스 (4-6주) ⚠️ Critical
  - [ ] Step 6.1: FastAPI Admin API (2주)
  - [ ] Step 6.2: React Admin Panel (2-3주)
  - [ ] Step 6.3: Docker & Nginx 통합 (3-5일)
- [ ] Phase 7: 템플릿 → 프론트엔드 (2-3주) (Optional)
- [ ] Phase 8: Django 종료 (1주)

### 예상 총 기간
- **최소**: 12주 (Phase 7 제외)
- **최대**: 18주 (Phase 7 포함)
- **Critical Path**: Phase 6 (관리 인터페이스) 성공 여부가 프로젝트 성패 결정
