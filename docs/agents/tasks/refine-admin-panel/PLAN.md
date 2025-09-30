# Refine Admin Panel — Implementation Plan

## Objective
Django Admin을 Refine (React) + FastAPI Admin API로 전환하여 Django 의존성 제거

## Constraints
- Django Admin 기능 동등 제공 (CRUD, 대량 작업, 파일 업로드)
- Phase 6.1 (FastAPI API) 2주, Phase 6.2 (Refine UI) 2-3주
- TDD: 각 Admin API 테스트 우선 작성
- 점진적 전환: Django Admin과 병렬 운영 (Phase 6 기간)

## Target Files & Changes

### Phase 6.1: FastAPI Admin API (2주)

#### Step 1: Admin 라우터 기반 구조 (1일)
**Goal**: Admin API 라우터 초기 설정, 권한 가드 적용

- [ ] **폴더 구조 생성**
  - `api/routers/admin/__init__.py`
  - `api/routers/admin/topics.py`
  - `api/routers/admin/contexts.py`
- [ ] **Admin 라우터 등록** (`api/main.py`)
  ```python
  from api.routers.admin import topics as admin_topics
  from api.routers.admin import contexts as admin_contexts

  app.include_router(admin_topics.router, prefix="/api/admin", tags=["admin"])
  app.include_router(admin_contexts.router, prefix="/api/admin", tags=["admin"])
  ```
- [ ] **권한 의존성 확인** (`api/dependencies/auth.py`)
  - `require_admin` 의존성 이미 구현 (Phase 5)
  - 모든 Admin API에 `Depends(require_admin)` 적용

**Validation**:
- `/api/admin/topics` 엔드포인트 존재 (401/403 응답)

---

#### Step 2: Topics Admin API — CRUD (2일)
**Goal**: Topic 관리 API 구현 (Refine 규약 준수)

- [ ] **Admin 스키마** (`api/schemas/admin.py` 생성)
  ```python
  class AdminTopicOut(BaseModel):
      id: int
      name: str
      description: str
      system_prompt: str
      contexts_count: int  # 계산 필드
      created_at: datetime
      updated_at: datetime

  class AdminTopicCreate(BaseModel):
      name: str
      description: str
      system_prompt: str
      context_ids: list[int] = []  # M2M 관계

  class AdminTopicUpdate(BaseModel):
      name: str | None = None
      description: str | None = None
      system_prompt: str | None = None
      context_ids: list[int] | None = None

  class TopicListResponse(BaseModel):
      data: list[AdminTopicOut]
      total: int
  ```

- [ ] **Topics Admin 라우터** (`api/routers/admin/topics.py`)
  ```python
  @router.get("/topics", response_model=TopicListResponse)
  async def list_topics(
      skip: int = 0,
      limit: int = 10,
      sort: str | None = None,  # "name_asc", "created_at_desc"
      filter: str | None = None,  # JSON string: {"name": "test"}
      db: Session = Depends(get_db),
      _: User = Depends(require_admin),
  ):
      # Refine 규약: data + total 반환
      query = db.query(Topic)

      # 필터 적용
      if filter:
          filters = json.loads(filter)
          if "name" in filters:
              query = query.filter(Topic.name.ilike(f"%{filters['name']}%"))

      # 정렬 적용
      if sort:
          field, order = sort.rsplit("_", 1)
          if order == "asc":
              query = query.order_by(getattr(Topic, field))
          else:
              query = query.order_by(getattr(Topic, field).desc())

      total = query.count()
      topics = query.offset(skip).limit(limit).all()

      return {"data": topics, "total": total}

  @router.get("/topics/{id}", response_model=AdminTopicOut)
  async def get_topic(...):
      ...

  @router.post("/topics", response_model=AdminTopicOut)
  async def create_topic(...):
      # context_ids로 M2M 관계 설정
      ...

  @router.put("/topics/{id}", response_model=AdminTopicOut)
  async def update_topic(...):
      ...

  @router.delete("/topics/{id}")
  async def delete_topic(...):
      ...
  ```

- [ ] **테스트** (`api/tests/admin/test_admin_topics.py`)
  ```python
  def test_list_topics_requires_admin(client, db_session):
      # 인증 없이 접근 → 401
      response = client.get("/api/admin/topics")
      assert response.status_code == 401

  def test_list_topics_with_admin(client, db_session, admin_headers):
      # admin 토큰으로 접근 → 200
      response = client.get("/api/admin/topics", headers=admin_headers)
      assert response.status_code == 200
      data = response.json()
      assert "data" in data
      assert "total" in data

  def test_create_topic_with_contexts(client, db_session, admin_headers):
      # Context 2개 생성
      ctx1 = SQLContext(name="Context 1", context_type="MARKDOWN")
      ctx2 = SQLContext(name="Context 2", context_type="FAQ")
      db_session.add_all([ctx1, ctx2])
      db_session.commit()

      # Topic 생성 (Context 연결)
      response = client.post(
          "/api/admin/topics",
          headers=admin_headers,
          json={
              "name": "Test Topic",
              "description": "Test",
              "system_prompt": "Prompt",
              "context_ids": [ctx1.id, ctx2.id],
          },
      )
      assert response.status_code == 201
      data = response.json()
      assert data["contexts_count"] == 2

  def test_update_topic_contexts(client, db_session, admin_headers):
      # Topic contexts 수정
      ...

  def test_list_topics_with_filter(client, db_session, admin_headers):
      # filter={"name": "test"}
      ...

  def test_list_topics_with_sort(client, db_session, admin_headers):
      # sort="name_asc"
      ...
  ```

**Validation**:
- Topics Admin CRUD 테스트 모두 통과
- Refine 규약 준수 (data + total)

---

#### Step 3: Contexts Admin API — CRUD (2일)
**Goal**: Context 관리 API 구현

- [ ] **Admin 스키마** (`api/schemas/admin.py`)
  ```python
  class AdminContextOut(BaseModel):
      id: int
      name: str
      description: str
      context_type: str
      original_content: str | None
      chunk_count: int
      processing_status: str
      created_at: datetime
      topics: list[AdminTopicOut]  # M2M 관계

  class AdminContextCreate(BaseModel):
      name: str
      description: str = ""
      context_type: str  # PDF, MARKDOWN, FAQ
      original_content: str | None = None  # MARKDOWN만
      topic_ids: list[int] = []

  class ContextListResponse(BaseModel):
      data: list[AdminContextOut]
      total: int
  ```

- [ ] **Contexts Admin 라우터** (`api/routers/admin/contexts.py`)
  - GET `/api/admin/contexts`: 목록 (필터, 정렬, 페이지네이션)
  - GET `/api/admin/contexts/{id}`: 상세 (청크 목록 포함)
  - POST `/api/admin/contexts`: 생성 (타입별 처리)
  - PUT `/api/admin/contexts/{id}`: 수정
  - DELETE `/api/admin/contexts/{id}`: 삭제

- [ ] **테스트** (`api/tests/admin/test_admin_contexts.py`)
  - CRUD 테스트
  - 타입별 생성 테스트 (PDF는 파일 없이 일단 생성만)
  - M2M 관계 테스트

**Validation**:
- Contexts Admin CRUD 테스트 모두 통과

---

#### Step 4: 대량 작업 API (2일)
**Goal**: Django Admin actions 포팅

- [ ] **대량 작업 스키마** (`api/schemas/admin.py`)
  ```python
  class BulkAssignRequest(BaseModel):
      context_ids: list[int]
      topic_id: int

  class BulkUpdateSystemPromptRequest(BaseModel):
      topic_ids: list[int]
      system_prompt: str

  class BulkRegenerateEmbeddingsRequest(BaseModel):
      context_ids: list[int]
  ```

- [ ] **대량 작업 라우터** (`api/routers/admin/bulk_operations.py`)
  ```python
  @router.post("/bulk/assign-contexts")
  async def bulk_assign_contexts(
      request: BulkAssignRequest,
      db: Session = Depends(get_db),
      _: User = Depends(require_admin),
  ):
      # Topic-Context M2M 대량 추가
      ...

  @router.post("/bulk/update-system-prompt")
  async def bulk_update_system_prompt(...):
      # Topic.system_prompt 일괄 수정
      ...

  @router.post("/bulk/regenerate-embeddings")
  async def bulk_regenerate_embeddings(...):
      # Django Celery task 트리거 (sync_to_async)
      from rag.tasks import regenerate_context_embeddings
      from asgiref.sync import sync_to_async

      for context_id in request.context_ids:
          await sync_to_async(regenerate_context_embeddings.delay)(context_id)

      return {"status": "queued", "count": len(request.context_ids)}
  ```

- [ ] **테스트** (`api/tests/admin/test_bulk_operations.py`)
  - 대량 할당 테스트
  - system_prompt 일괄 수정 테스트
  - 임베딩 재생성 테스트 (Celery task 호출 확인)

**Validation**:
- 대량 작업 API 테스트 통과

---

#### Step 5: 파일 업로드 & SSE 처리 상태 (3일)
**Goal**: PDF 업로드 → 처리 → SSE 스트리밍

- [ ] **파일 업로드 엔드포인트** (`api/routers/admin/contexts.py`)
  ```python
  @router.post("/contexts/upload")
  async def upload_pdf(
      file: UploadFile,
      name: str = Form(...),
      description: str = Form(""),
      topic_ids: str = Form("[]"),  # JSON array string
      db: Session = Depends(get_db),
      _: User = Depends(require_admin),
  ):
      # 1. Context 생성 (processing_status="PENDING")
      context = SQLContext(
          name=name,
          description=description,
          context_type="PDF",
          processing_status="PENDING",
      )
      db.add(context)
      db.commit()

      # 2. 파일 임시 저장
      file_path = f"/tmp/{context.id}_{file.filename}"
      with open(file_path, "wb") as f:
          f.write(await file.read())

      # 3. Django Celery task 트리거
      from rag.tasks import process_pdf_context
      from asgiref.sync import sync_to_async

      await sync_to_async(process_pdf_context.delay)(context.id, file_path)

      return {"id": context.id, "status": "processing"}
  ```

- [ ] **처리 상태 SSE 엔드포인트** (`api/routers/admin/contexts.py`)
  ```python
  from fastapi.responses import StreamingResponse
  import asyncio

  @router.get("/contexts/{id}/status-stream")
  async def stream_processing_status(
      id: int,
      db: Session = Depends(get_db),
      _: User = Depends(require_admin),
  ):
      async def event_generator():
          while True:
              context = db.query(SQLContext).filter_by(id=id).first()
              if not context:
                  yield f"data: {json.dumps({'error': 'not found'})}\n\n"
                  break

              status = {
                  "id": context.id,
                  "processing_status": context.processing_status,
                  "chunk_count": context.chunk_count,
              }
              yield f"data: {json.dumps(status)}\n\n"

              if context.processing_status in ["COMPLETED", "FAILED"]:
                  break

              await asyncio.sleep(1)

      return StreamingResponse(
          event_generator(),
          media_type="text/event-stream",
      )
  ```

- [ ] **테스트** (`api/tests/admin/test_file_upload.py`)
  ```python
  def test_upload_pdf_requires_admin(client):
      response = client.post("/api/admin/contexts/upload", files={...})
      assert response.status_code == 401

  @patch("rag.tasks.process_pdf_context.delay")
  def test_upload_pdf_triggers_celery(mock_task, client, admin_headers):
      response = client.post(
          "/api/admin/contexts/upload",
          headers=admin_headers,
          files={"file": ("test.pdf", b"PDF content", "application/pdf")},
          data={"name": "Test PDF", "description": "Test"},
      )
      assert response.status_code == 200
      assert mock_task.called

  def test_sse_status_stream(client, db_session, admin_headers):
      # Context 생성 (PENDING)
      ctx = SQLContext(..., processing_status="PENDING")
      db_session.add(ctx)
      db_session.commit()

      # SSE 스트림 시작
      with client.stream("GET", f"/api/admin/contexts/{ctx.id}/status-stream", headers=admin_headers) as response:
          lines = []
          for line in response.iter_lines():
              lines.append(line)
              if len(lines) >= 2:  # 최소 2개 이벤트
                  break

          # 첫 번째 이벤트 확인
          assert "PENDING" in lines[0]
  ```

**Validation**:
- 파일 업로드 → Celery task 트리거 확인
- SSE 스트림 동작 확인

---

#### Step 6: 통합 테스트 (1일)
- [ ] 전체 Admin API 테스트 실행 (`uv run pytest api/tests/admin/`)
- [ ] Swagger UI (`/docs`)에서 수동 테스트
  - Admin 토큰 발급 (`/api/auth/login`)
  - Topic CRUD
  - Context CRUD + 파일 업로드
  - 대량 작업

**Validation**:
- 모든 Admin API 테스트 통과
- Django Admin 기능 동등성 확인

---

## Test/Validation Cases

### Topics Admin API
- [ ] 인증 없이 접근 → 401
- [ ] 일반 사용자 접근 → 403
- [ ] Admin 사용자 CRUD 성공
- [ ] Context M2M 관계 설정
- [ ] 필터/정렬/페이지네이션

### Contexts Admin API
- [ ] CRUD 테스트
- [ ] 타입별 생성 (PDF/MARKDOWN/FAQ)
- [ ] Topic M2M 관계
- [ ] 청크 통계 표시

### 대량 작업
- [ ] Context 대량 할당
- [ ] system_prompt 일괄 수정
- [ ] 임베딩 재생성 (Celery 호출)

### 파일 업로드
- [ ] PDF 업로드 → Context 생성
- [ ] Celery task 트리거
- [ ] SSE 상태 스트리밍

## Steps

1. [1일] Admin 라우터 기반 구조
2. [2일] Topics Admin CRUD
3. [2일] Contexts Admin CRUD
4. [2일] 대량 작업 API
5. [3일] 파일 업로드 & SSE
6. [1일] 통합 테스트

**총 기간**: 11일 (약 2주)

## Rollback
- Admin API는 기존 API와 독립적 → 제거 시 영향 없음
- Django Admin 계속 사용 가능

## Review Hotspots
- **Refine 규약 준수**: `{ data, total }` 형식 엄수
- **권한 검사**: 모든 Admin API에 `require_admin` 적용
- **Celery 통합**: `sync_to_async` 사용, task 실패 처리
- **SSE 연결 관리**: 클라이언트 연결 해제 시 정리

## Status
- [ ] Step 1: 라우터 기반 구조
- [ ] Step 2: Topics Admin CRUD
- [ ] Step 3: Contexts Admin CRUD
- [ ] Step 4: 대량 작업 API
- [ ] Step 5: 파일 업로드 & SSE
- [ ] Step 6: 통합 테스트
