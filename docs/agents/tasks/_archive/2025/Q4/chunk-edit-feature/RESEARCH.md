# Research: 청크 레벨 편집 기능

## Goal
Context 상세 페이지 내 개별 ContextItem(청크) 편집 UI/API 구현.

## Scope
- Backend: PUT/PATCH /contexts/{cid}/items/{iid} 엔드포인트 + 스키마 + validation + TDD
- Frontend: 청크 테이블 내 inline edit 또는 모달 UI

## Related Files/Flows
- `backend/routers/admin/contexts.py`: `GET /contexts/{id}/items` 이미 존재 (task chunk-preview-ui)
- `backend/models/context.py`: ContextItem (id, context_id, content, vector, metadata, order_index)
- `backend/schemas/admin.py`: AdminContextItemOut (미리보기용)
- `frontend/src/pages/contexts/show.tsx`: 청크 테이블 렌더링 (`/api/admin/contexts/{id}/items`)

## Hypotheses
1. **편집 가능 필드**: `content`, `metadata.source_page` (PDF), `order_index` → 나머지는 읽기전용.
2. **Embedding 재생성**: `content` 수정 시 `vector`도 재생성 필요 (OpenAI embeddings).
3. **Validation**: `content` not empty, `order_index` unique per context, metadata JSON validation.
4. **Frontend 옵션**:
   - Option A: 각 행에 "편집" 버튼 → 모달 폼 열기 (shadcn Dialog + Form)
   - Option B: inline editing (table cell → input), 복잡도 높음.

## Evidence
- `backend/routers/admin/contexts.py:L124-151` (GET items 구현):
  - Pagination 지원, `db.query(ContextItem).filter(...).order_by(order_index).limit(10)`
  - Response: `{"total": int, "items": [AdminContextItemOut]}`
- `backend/models/context.py:L57-76` (ContextItem):
  - `id` (int PK), `context_id`, `content`, `vector`, `metadata` (JSON), `order_index`, timestamps
  - `embeddings` relationship (ContextItemEmbedding → Qdrant UUID 참조)
- `backend/schemas/admin.py:L73-84` (AdminContextItemOut):
  - `id`, `content`, `metadata`, `order_index`, `created_at`, `updated_at`
  - `Config: from_attributes=True` (ORM read 용)
- `frontend/src/pages/contexts/show.tsx:L189-221` (Table):
  - Columns: 순서, 내용 미리보기, 페이지, 길이
  - Pagination 10개씩
- Embedding 재생성: `backend/retrieval/embeddings.py:L15-24` (`generate_embeddings_batch`) → OpenAI API 호출

## Assumptions/Open Questions
- **Q1**: `order_index` 수정 시 context 내 다른 청크들 재정렬 필요? → **A**: 일단 manual update만 지원 (drag-and-drop은 later).
- **Q2**: Embedding 재생성 시 Qdrant 기존 벡터도 업데이트? → **A**: Yes, ContextItemEmbedding 테이블에서 UUID 찾아 Qdrant upsert.
- **Q3**: Celery 대신 sync 처리? → **A**: Yes (Phase 4에서 Celery 제거 확정, TASKS.md:L38).
- **Q4**: 편집 권한? → **A**: Admin only (`require_admin` 의존성).

## Risks
1. **Embedding 재생성 latency**: OpenAI API 호출 → 청크 하나당 ~500ms; sync 처리 시 blocking.
2. **Qdrant 업데이트 실패**: transactional 롤백 필요 (DB commit 전 Qdrant upsert 시도).
3. **Frontend UX**: 모달 폼 vs inline edit 선택 → 모달이 구현 단순.

## Next
→ PLAN.md 작성: API 엔드포인트 설계, 스키마 정의, TDD 단계별 계획.
