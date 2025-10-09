# Research: Add Missing Indexes

## Goal
DB에 누락된 인덱스 식별 및 쿼리 패턴 검증

## Scope
- `rag_topic.slug` (unique btree 존재, but 개별 index 재확인)
- `rag_contextitem.order_index` (미존재)
- `rag_questionhistory.session_id` (btree 존재)

## Related Files
- `backend/models/topic.py:26-27` — slug column (unique=True, index=True)
- `backend/models/context.py:71` — order_index column (no index)
- `backend/models/history.py:28` — session_id column (index=True)

## Query Patterns

### topics.slug
- `backend/routers/topics.py` — slug 기반 라우팅 (`/topics/{slug}`)
- `backend/services/slug_utils.py` — ensure_unique_slug 중복 검사 쿼리

### order_index
- `backend/routers/admin/contexts.py:308-309` — PATCH `/admin/contexts/{context_id}/items/{item_id}` 업데이트
- `backend/tests/admin/test_admin_contexts.py:358-400` — order_index 업데이트 테스트
- **실제 정렬 쿼리 부재**: 현재 `Context.items` relationship은 `order_by` 미지정

### session_id
- `backend/routers/history.py:64` — `GET /history?session_id={session_id}` 필터
- `backend/routers/history.py:108` — `GET /history/session/{session_id}` 세션별 조회
- `backend/routers/admin/analytics.py:32` — `count(distinct(session_id))` 집계

## Evidence (Postgres Schema)

### rag_topic
```
Indexes:
    "ix_rag_topic_slug" btree (slug)
    "uq_rag_topic_slug" UNIQUE CONSTRAINT, btree (slug)
```
**결론**: slug는 이미 btree + unique 인덱스 존재. **추가 불필요**.

### rag_contextitem
```
Indexes:
    "rag_contextitem_pkey" PRIMARY KEY, btree (id)
    "ix_rag_contextitem_context_id" btree (context_id)
    "ix_rag_contextitem_id" btree (id)
```
**결론**: `order_index` 인덱스 **부재**. 정렬 쿼리 시 필요.

### rag_questionhistory
```
Indexes:
    "ix_rag_questionhistory_session_id" btree (session_id)
    "ix_rag_questionhistory_topic_id" btree (topic_id)
```
**결론**: `session_id` 인덱스 **이미 존재**. 추가 불필요.

## Assumptions/Open Qs
- **order_index 정렬 쿼리 추가 필요?** — 현재 `Context.items` relationship에 `order_by="ContextItem.order_index"` 누락. 모델 수정도 고려해야 함.

## Risks
- **order_index 인덱스만 추가**할 경우, relationship `order_by` 누락 시 실효성 낮음.

## Next
- **Scope 축소**: `rag_contextitem.order_index` 인덱스만 추가.
- **Bonus (선택)**: `Context.items` relationship에 `order_by="ContextItem.order_index"` 추가 (별도 커밋).
