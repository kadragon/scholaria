# Refine Admin Panel — Research

## Goal
Django Admin을 Refine (React) + FastAPI Admin API로 전환하여 헤드리스 아키텍처 구현

## Scope
- Django Admin 기능 분석 (CRUD, 대량 작업, 파일 업로드, 타입별 워크플로우)
- FastAPI Admin API 설계 (권한, 스키마, 엔드포인트)
- Refine 통합 전략 (Data Provider, Auth Provider)

## Related Files/Flows

### Django Admin 현황
- **Admin 클래스**: `rag/admin.py` (TopicAdmin, ContextAdmin)
- **대량 작업**: `bulk_assign_context`, `bulk_update_system_prompt`, `regenerate_embeddings`
- **커스텀 뷰**: `add_qa_pair`, `bulk_assign_context_view`
- **파일 업로드**: ContextAdmin에서 PDF 업로드 → Celery 비동기 처리
- **타입별 폼**: Context 타입에 따라 동적 폼 필드 (PDF: file, FAQ: none, Markdown: original_content)

### 기존 FastAPI API
- **Phase 2-4**: Topics/Contexts Read/Write API 이미 구현
  - GET/POST/PUT/DELETE `/api/topics`, `/api/contexts`
  - Phase 5: JWT 인증 (require_admin 의존성)
- **부족한 기능**:
  - 대량 작업 엔드포인트 없음
  - Admin 전용 필드 노출 안 됨 (예: processing_status, chunk_count 상세)
  - 파일 업로드 처리 상태 스트리밍 없음

## Hypotheses

### H1: FastAPI Admin API는 별도 라우터 vs. 기존 API 확장
- **Option A (별도 라우터)**: `/api/admin/topics`, `/api/admin/contexts`
  - 장점: 권한 분리 명확, 일반 API와 Admin API 독립적 버전 관리
  - 단점: 중복 코드 가능성
- **Option B (기존 API 확장)**: `/api/topics?admin=true` (query param)
  - 장점: 코드 재사용
  - 단점: 일반 API와 Admin API 혼재, 복잡도 증가
- **결론**: **Option A 선택** (권한 분리 및 확장성)

### H2: Refine Data Provider — REST vs. GraphQL
- **REST**: Refine의 `@refinedev/simple-rest` 사용
  - 장점: FastAPI와 완벽 호환, 간단한 설정
  - 단점: N+1 쿼리 가능성 (관계 데이터 로드 시)
- **GraphQL**: Strawberry GraphQL + Refine GraphQL Provider
  - 장점: 유연한 쿼리, N+1 해결
  - 단점: 추가 학습 곡선, FastAPI-SQLAlchemy 통합 복잡
- **결론**: **REST 선택** (단순성 우선, 필요 시 후에 최적화)

### H3: 파일 업로드 처리 상태 — 폴링 vs. SSE vs. WebSocket
- **폴링**: 클라이언트가 주기적으로 상태 확인 (GET `/api/admin/contexts/{id}/status`)
  - 장점: 구현 간단
  - 단점: 불필요한 요청 증가
- **SSE (Server-Sent Events)**: 서버가 상태 푸시 (EventSource API)
  - 장점: 실시간 업데이트, HTTP 기반 (방화벽 문제 없음)
  - 단점: 단방향 통신
- **WebSocket**: 양방향 통신
  - 장점: 실시간 양방향
  - 단점: 복잡도 증가, FastAPI WebSocket 관리
- **결론**: **SSE 선택** (실시간 + 단순성, PDF 업로드는 단방향만 필요)

## Evidence

### Django Admin 기능 목록 (rag/admin.py 분석)
```python
# TopicAdmin
- list_display: name, description, system_prompt, contexts_count
- actions: bulk_update_system_prompt
- inline: Context 다중 선택 (M2M)

# ContextAdmin
- list_display: name, context_type, chunk_count, processing_status, created_at
- actions: bulk_assign_context, regenerate_embeddings, bulk_update_processing_status
- custom_views: add_qa_pair (FAQ 전용)
- file_upload: PDF 업로드 → Celery task
```

### Refine 기본 구조
```typescript
// Data Provider Interface (REST)
interface DataProvider {
  getList: (resource, params) => Promise<{ data, total }>;
  getOne: (resource, params) => Promise<{ data }>;
  create: (resource, params) => Promise<{ data }>;
  update: (resource, params) => Promise<{ data }>;
  deleteOne: (resource, params) => Promise<{ data }>;
  // Custom methods
  custom?: (params) => Promise<any>;
}
```
- **Refine REST 규약**:
  - GET `/api/admin/topics` → `{ data: Topic[], total: number }`
  - GET `/api/admin/topics/{id}` → `{ data: Topic }`
  - POST `/api/admin/topics` → `{ data: Topic }`
  - PUT `/api/admin/topics/{id}` → `{ data: Topic }`
  - DELETE `/api/admin/topics/{id}` → `{ data: Topic }`

## Assumptions/Open Qs

### 가정
1. **권한 모델 단순화**: 초기 구현은 `is_staff` 만 확인 (role 기반은 향후 확장)
2. **Celery 유지**: PDF 처리는 여전히 Django Celery 사용 (FastAPI → Django ORM signal 제한)
3. **점진적 전환**: Django Admin과 Refine Admin 병렬 운영 (Phase 6 기간 동안)

### 열린 질문
1. **Refine UI 프레임워크**: shadcn/ui vs. Material-UI vs. Ant Design?
   - **추천**: shadcn/ui (Tailwind 기반, 커스터마이징 용이, 모던)
2. **대량 작업 UX**: 선택 → 작업 버튼 → 확인 다이얼로그 (Django Admin과 동일)
3. **청크 미리보기**: Drawer (슬라이드 패널) vs. Modal?
   - **추천**: Drawer (컨텍스트 유지, 스크롤 가능)

## Sub-agent Findings
없음 (단일 에이전트로 충분)

## Risks

### High
- **개발 기간**: Phase 6 전체 4-6주 예상 (프론트엔드 리소스 필요)
  - 완화: Phase 6.1 (FastAPI API) 먼저 완료, Phase 6.2 (Refine)는 병렬 진행 가능

### Medium
- **Celery 의존성**: FastAPI에서 Django signal 호출 불가 → PDF 처리는 Django Celery 유지
  - 완화: FastAPI Admin API는 Context 생성만, 실제 처리는 Django Celery task 트리거

### Low
- **Refine 학습 곡선**: React 기반, 새로운 프레임워크
  - 완화: Refine은 헤드리스 설계로 학습 곡선 낮음 (공식 문서 우수)

## Next
**PLAN.md 작성** → Phase 6.1 FastAPI Admin API 구현 계획 (Topics CRUD 우선)
