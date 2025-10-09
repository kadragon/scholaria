# Admin API Specification

## Context & Goal

**Context**: Scholaria의 Refine Admin Panel을 위한 FastAPI Admin API입니다. Django Admin을 대체하여 Topic, Context 관리 및 대량 작업(bulk operations)을 제공합니다. Phase 6에서 구현되며, Phase 8에서 Django 완전 제거를 목표로 합니다.

**Goal**: 관리자가 Topic/Context CRUD, 파일 업로드, 대량 작업(토픽 할당, 임베딩 재생성, 시스템 프롬프트 업데이트)을 수행할 수 있는 REST API를 제공합니다. Refine의 Data Provider와 완벽히 통합됩니다.

## Scope

**In Scope**:
- Admin Topic CRUD (`/api/admin/topics`)
- Admin Context CRUD (`/api/admin/contexts`)
- 파일 업로드 (PDF/Markdown/FAQ)
- 처리 상태 폴링 (`/api/admin/contexts/{id}/processing-status`)
- 대량 작업 (`/api/admin/bulk/...`)
  - Context → Topic 할당
  - 임베딩 재생성 (Celery 트리거)
  - 시스템 프롬프트 대량 업데이트
- 관리자 인증 (`require_admin` 의존성)

**Out of Scope**:
- 사용자 관리 (Django Admin에서 처리)
- 감사 로그 (Audit Log)
- 권한 세분화 (RBAC) — 초기에는 is_staff=True만 확인

## Contract

### 1. Admin Topics API

#### GET `/api/admin/topics`

Topic 목록 조회 (페이지네이션).

**Query Parameters**:
- `page`: 페이지 번호 (default: 1)
- `per_page`: 페이지당 항목 수 (default: 20)
- `sort`: 정렬 필드 (default: "id")
- `order`: 정렬 순서 ("asc" | "desc", default: "asc")

**응답 (200 OK)**:
```json
{
  "data": [
    {
      "id": 1,
      "name": "Anthropic Docs",
      "system_prompt": "You are an expert on Anthropic...",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 10
}
```

**Pydantic Schema**:
```python
class AdminTopicOut(BaseModel):
    id: int
    name: str
    system_prompt: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AdminTopicListResponse(BaseModel):
    data: list[AdminTopicOut]
    total: int
```

#### POST `/api/admin/topics`

Topic 생성 (관리자 권한 필요).

**요청 (JSON)**:
```json
{
  "name": "New Topic",
  "system_prompt": "You are an expert..."
}
```

**Pydantic Schema**:
```python
class AdminTopicIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    system_prompt: str | None = None
```

**응답 (201 CREATED)**:
```json
{
  "id": 2,
  "name": "New Topic",
  "system_prompt": "You are an expert...",
  "created_at": "2025-10-10T08:00:00Z",
  "updated_at": "2025-10-10T08:00:00Z"
}
```

**에러**:
- `401 UNAUTHORIZED`: 토큰 없음/만료
- `403 FORBIDDEN`: is_staff=False
- `400 BAD REQUEST`: 잘못된 입력 (빈 name)

#### PUT `/api/admin/topics/{id}`

Topic 수정 (관리자 권한 필요).

**요청 (JSON)**:
```json
{
  "name": "Updated Topic",
  "system_prompt": "Updated prompt..."
}
```

**응답 (200 OK)**: AdminTopicOut

**에러**:
- `404 NOT FOUND`: Topic ID 존재하지 않음

#### DELETE `/api/admin/topics/{id}`

Topic 삭제 (관리자 권한 필요).

**응답 (204 NO CONTENT)**

**에러**:
- `404 NOT FOUND`: Topic ID 존재하지 않음
- `400 BAD REQUEST`: Topic에 연결된 Context 존재 (Cascade 정책에 따라 변경 가능)

### 2. Admin Contexts API

#### GET `/api/admin/contexts`

Context 목록 조회 (페이지네이션, 필터링).

**Query Parameters**:
- `page`, `per_page`, `sort`, `order` (Topics와 동일)
- `topic_id`: Topic 필터 (optional)
- `context_type`: 타입 필터 ("PDF" | "MARKDOWN" | "FAQ", optional)

**응답 (200 OK)**:
```json
{
  "data": [
    {
      "id": 1,
      "name": "Anthropic Overview",
      "description": "Company overview document",
      "context_type": "PDF",
      "topics": [
        {"id": 1, "name": "Anthropic Docs"}
      ],
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 50
}
```

**Pydantic Schema**:
```python
class AdminTopicSummary(BaseModel):
    id: int
    name: str

class AdminContextOut(BaseModel):
    id: int
    name: str
    description: str
    context_type: str  # "PDF" | "MARKDOWN" | "FAQ"
    topics: list[AdminTopicSummary]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AdminContextListResponse(BaseModel):
    data: list[AdminContextOut]
    total: int
```

#### POST `/api/admin/contexts`

Context 생성 (타입별 분기, 파일 업로드 지원).

**요청 (Multipart Form Data)**:
```
name: string (required)
description: string (optional)
context_type: "PDF" | "MARKDOWN" | "FAQ" (required)
file: File (PDF만 필수)
content: string (MARKDOWN만 필수)
qa_pairs: JSON string (FAQ만 필수)
```

**Pydantic Schema**:
```python
class AdminContextIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    context_type: Literal["PDF", "MARKDOWN", "FAQ"]
    # 파일/콘텐츠는 FastAPI UploadFile/Form으로 처리
```

**응답 (201 CREATED)**:
```json
{
  "id": 10,
  "name": "New Context",
  "description": "",
  "context_type": "PDF",
  "topics": [],
  "created_at": "2025-10-10T08:00:00Z",
  "updated_at": "2025-10-10T08:00:00Z"
}
```

**에러**:
- `400 BAD REQUEST`: 파일 누락 (PDF), 콘텐츠 누락 (MARKDOWN), 잘못된 형식
- `413 PAYLOAD TOO LARGE`: 파일 크기 > 100MB

#### GET `/api/admin/contexts/{id}/processing-status`

Context 처리 상태 조회 (파일 업로드 후 폴링용).

**응답 (200 OK)**:
```json
{
  "status": "PROCESSING",
  "progress": 45,
  "message": "Extracting PDF pages..."
}
```

**Status Values**:
- `PENDING`: 대기 중
- `PROCESSING`: 처리 중
- `COMPLETED`: 완료
- `FAILED`: 실패

**Pydantic Schema**:
```python
class ProcessingStatus(BaseModel):
    status: Literal["PENDING", "PROCESSING", "COMPLETED", "FAILED"]
    progress: int = Field(..., ge=0, le=100)
    message: str = ""
```

#### PUT `/api/admin/contexts/{id}`

Context 수정.

**요청 (JSON)**:
```json
{
  "name": "Updated Context",
  "description": "Updated description"
}
```

**응답 (200 OK)**: AdminContextOut

#### DELETE `/api/admin/contexts/{id}`

Context 삭제 (연관된 ContextItem, 임베딩 자동 삭제 via CASCADE).

**응답 (204 NO CONTENT)**

### 3. Bulk Operations API

#### POST `/api/admin/bulk/assign-context-to-topic`

여러 Context를 하나의 Topic에 할당.

**요청 (JSON)**:
```json
{
  "context_ids": [1, 2, 3],
  "topic_id": 5
}
```

**Pydantic Schema**:
```python
class BulkAssignContextRequest(BaseModel):
    context_ids: list[int] = Field(..., min_length=1)
    topic_id: int = Field(..., gt=0)
```

**응답 (200 OK)**:
```json
{
  "updated_count": 3
}
```

**에러**:
- `400 BAD REQUEST`: 빈 context_ids
- `404 NOT FOUND`: topic_id 존재하지 않음
- `404 NOT FOUND`: 일부 context_id 존재하지 않음 (부분 적용 가능 여부는 구현 정책)

#### POST `/api/admin/bulk/regenerate-embeddings`

여러 Context의 임베딩 재생성 (Celery 비동기 작업 트리거).

**요청 (JSON)**:
```json
{
  "context_ids": [1, 2, 3]
}
```

**Pydantic Schema**:
```python
class BulkRegenerateEmbeddingsRequest(BaseModel):
    context_ids: list[int] = Field(..., min_length=1)
```

**응답 (202 ACCEPTED)**:
```json
{
  "task_ids": [
    "abc123-task-1",
    "def456-task-2",
    "ghi789-task-3"
  ],
  "message": "3 embedding regeneration tasks queued"
}
```

**에러**:
- `400 BAD REQUEST`: 빈 context_ids
- `503 SERVICE UNAVAILABLE`: Celery 연결 실패

#### POST `/api/admin/bulk/update-system-prompt`

여러 Topic의 system_prompt 대량 업데이트.

**요청 (JSON)**:
```json
{
  "topic_ids": [1, 2, 3],
  "system_prompt": "New unified prompt for all topics..."
}
```

**Pydantic Schema**:
```python
class BulkUpdateSystemPromptRequest(BaseModel):
    topic_ids: list[int] = Field(..., min_length=1)
    system_prompt: str = Field(..., min_length=1)
```

**응답 (200 OK)**:
```json
{
  "updated_count": 3
}
```

**에러**:
- `400 BAD REQUEST`: 빈 topic_ids 또는 빈 system_prompt
- `404 NOT FOUND`: 일부 topic_id 존재하지 않음

## Examples

### Example 1: Topic 생성

```bash
# 로그인 (JWT 토큰 획득)
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=admin&password=admin123"

# 응답
{"access_token": "eyJhbGci...", "token_type": "bearer"}

# Topic 생성
curl -X POST http://localhost:8000/api/admin/topics \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Safety",
    "system_prompt": "You are an expert on AI safety research..."
  }'

# 응답 (201 CREATED)
{
  "id": 5,
  "name": "AI Safety",
  "system_prompt": "You are an expert on AI safety research...",
  "created_at": "2025-10-10T08:00:00Z",
  "updated_at": "2025-10-10T08:00:00Z"
}
```

### Example 2: PDF 업로드

```bash
curl -X POST http://localhost:8000/api/admin/contexts \
  -H "Authorization: Bearer eyJhbGci..." \
  -F "name=AI Safety Paper" \
  -F "description=Research paper on AI alignment" \
  -F "context_type=PDF" \
  -F "file=@/path/to/paper.pdf"

# 응답 (201 CREATED)
{
  "id": 10,
  "name": "AI Safety Paper",
  "description": "Research paper on AI alignment",
  "context_type": "PDF",
  "topics": [],
  "created_at": "2025-10-10T08:00:00Z",
  "updated_at": "2025-10-10T08:00:00Z"
}

# 처리 상태 폴링
curl http://localhost:8000/api/admin/contexts/10/processing-status \
  -H "Authorization: Bearer eyJhbGci..."

# 응답 (200 OK)
{"status": "PROCESSING", "progress": 60, "message": "Generating embeddings..."}

# 1-2초 후 재시도
{"status": "COMPLETED", "progress": 100, "message": ""}
```

### Example 3: 대량 작업 (Bulk Assign)

```bash
# 5개 Context를 Topic 3에 할당
curl -X POST http://localhost:8000/api/admin/bulk/assign-context-to-topic \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{
    "context_ids": [1, 2, 3, 4, 5],
    "topic_id": 3
  }'

# 응답 (200 OK)
{"updated_count": 5}
```

### Example 4: 임베딩 재생성 (Bulk Regenerate)

```bash
curl -X POST http://localhost:8000/api/admin/bulk/regenerate-embeddings \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{
    "context_ids": [1, 2, 3]
  }'

# 응답 (202 ACCEPTED)
{
  "task_ids": ["abc123", "def456", "ghi789"],
  "message": "3 embedding regeneration tasks queued"
}
```

## Acceptance Criteria

### AC1: Admin Topics CRUD

- [x] GET /api/admin/topics (페이지네이션, 정렬)
- [x] POST /api/admin/topics (관리자 권한)
- [x] PUT /api/admin/topics/{id} (관리자 권한)
- [x] DELETE /api/admin/topics/{id} (관리자 권한)
- [x] 관리자가 아닌 사용자 요청 시 403

### AC2: Admin Contexts CRUD

- [x] GET /api/admin/contexts (페이지네이션, 필터링: topic_id, context_type)
- [x] POST /api/admin/contexts (파일 업로드 지원: PDF/MARKDOWN/FAQ)
- [x] GET /api/admin/contexts/{id}/processing-status (PENDING → PROCESSING → COMPLETED)
- [x] PUT /api/admin/contexts/{id}
- [x] DELETE /api/admin/contexts/{id} (CASCADE 삭제)

### AC3: Bulk Operations

- [x] POST /bulk/assign-context-to-topic (5개 Context → 1 Topic)
- [x] POST /bulk/regenerate-embeddings (Celery 작업 트리거)
- [x] POST /bulk/update-system-prompt (3개 Topic 일괄 업데이트)
- [x] 빈 ID 목록은 400 에러

### AC4: 파일 업로드

- [x] PDF 업로드 (max 100MB)
- [x] 처리 상태 폴링 (status, progress, message)
- [x] 업로드 후 자동 chunking + embedding 생성 (Celery)

### AC5: Refine Data Provider 호환

- [x] 응답 형식: `{data: [...], total: N}` (list 엔드포인트)
- [x] 페이지네이션: `page`, `per_page` query params
- [x] 정렬: `sort`, `order` query params
- [x] 에러 응답: HTTP 표준 상태 코드 + JSON detail

## Dependencies

| Name | Latest | Chosen | Rationale | Link |
|------|--------|--------|-----------|------|
| @refinedev/core | 4.54.0 | 4.54.0 | Refine 핵심 라이브러리 | https://refine.dev/ |
| @refinedev/simple-rest | 4.5.8 | 4.5.8 | REST Data Provider | https://refine.dev/docs/data/packages/simple-rest/ |
| celery | 5.4.0 | 5.4.0 | 비동기 작업 큐 (이미 설치됨) | https://docs.celeryq.dev/ |
| python-multipart | 0.0.20 | 0.0.20 | FastAPI 파일 업로드 (이미 설치됨) | https://github.com/andrew-d/python-multipart |

## Versioning & Migration

### Version: 1.0.0 (Initial Implementation)

**릴리스**: Phase 6 (2025-10-01~2025-10-15)

**변경사항**:
- Admin Topics CRUD API
- Admin Contexts CRUD API (파일 업로드 포함)
- 대량 작업 3종 (assign, regenerate, update-prompt)
- 처리 상태 폴링 엔드포인트

**마이그레이션**:
- **DB 마이그레이션**: 불필요 (기존 모델 사용)
- **Django Admin**: Phase 6 기간 동안 병행 운영
- **Refine Admin**: 신규 프론트엔드 프로젝트 (`admin-frontend/`)

**하위 호환성**: Django Admin과 독립적으로 운영 가능

### Future: Version 2.0.0 (Advanced Features)

**계획**:
- 감사 로그 (Audit Log): CRUD 작업 기록
- 권한 세분화 (RBAC): is_staff 외 추가 역할 (viewer, editor, admin)
- 실시간 진행 상황 (WebSocket): 파일 처리 진행 상황 푸시
- Context Preview: PDF/Markdown 미리보기

## Performance

### Latency Targets

| 엔드포인트 | P95 목표 | 설명 |
|-----------|---------|------|
| GET /admin/topics | < 200ms | 페이지당 20개, 인덱스 활용 |
| GET /admin/contexts | < 300ms | JOIN (topics), 페이지당 20개 |
| POST /admin/topics | < 100ms | 단순 INSERT |
| POST /admin/contexts (PDF) | < 2s | 파일 저장 + Celery 트리거 (비동기) |
| POST /bulk/assign | < 500ms | UPDATE N개 (N < 100) |
| POST /bulk/regenerate | < 200ms | Celery 트리거만 (실제 작업은 비동기) |

### Throughput

- **동시 관리자**: 5-10명 예상
- **대량 작업**: Context 100개 동시 할당 < 1초
- **파일 업로드**: 동시 5개 업로드 처리 가능 (Celery 워커 수 기준)

### Caching

- **Admin 데이터**: 캐싱 불필요 (관리자 수 적음, 데이터 변경 빈번)
- **처리 상태**: Redis에 캐싱 가능 (TTL 300초)

## Security Considerations

### 1. Admin 권한 검증

**리스크**: is_staff=False 사용자가 관리 작업 수행

**완화**:
- 모든 Admin 엔드포인트에 `require_admin` 의존성 적용
- `require_admin`은 `is_staff=True` 확인
- 테스트: `test_admin_requires_staff.py` (403 검증)

### 2. 파일 업로드 보안

**리스크**: 악의적 파일 업로드 (XXE, RCE)

**완화**:
- Content-Type 검증: `application/pdf`만 허용
- 파일 크기 제한: 100MB
- 파일명 sanitization: 경로 traversal 방지
- 파일 스캔: (향후) ClamAV 통합

### 3. 대량 작업 남용

**리스크**: 관리자가 실수로 전체 Context 삭제

**완화**:
- Bulk 작업 ID 개수 제한 (max 100개)
- 삭제 작업은 확인 단계 추가 (프론트엔드)
- 감사 로그 (향후)

### 4. Celery 작업 보안

**리스크**: 악의적 task_id로 Celery 명령 실행

**완화**:
- Celery task는 서버에서만 생성 (`task.delay()`)
- 사용자 입력은 task argument로만 전달
- Redis 인증 활성화

## References

- **PLAN**: `.tasks/refine-admin-panel/PLAN.md` (Refine Admin 구현 계획)
- **Tests**: `backend/tests/admin/test_*.py` (Admin API 테스트)
- **Auth SPEC**: `.spec/backend/auth.spec.md` (JWT 인증 사양)
- **Refine Data Provider**: https://refine.dev/docs/data/data-provider/
- **FastAPI File Upload**: https://fastapi.tiangolo.com/tutorial/request-files/
