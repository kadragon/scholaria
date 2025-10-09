# Progress: Add Missing Indexes

## Summary
`rag_contextitem.order_index` btree 인덱스 추가 완료. Alembic 마이그레이션 0004 생성 및 up/down 검증 완료.

## Goal & Approach
- **Goal**: 정렬 쿼리 성능 향상을 위한 `order_index` 인덱스 추가
- **Approach**: TDD로 테스트 먼저 작성 → 마이그레이션 스크립트 작성 → 검증 (upgrade/downgrade/idempotency)

## Completed Steps

### Step 1: Research & Planning (Completed)
- DB 스키마 검증: `topics.slug` (이미 존재), `session_id` (이미 존재), `order_index` (부재)
- 최종 스코프: `rag_contextitem.order_index` 단일 인덱스 추가

### Step 2: Write Tests (Completed)
- `backend/tests/test_alembic_migrations.py` 작성 (3개 테스트)
  - `test_0004_order_index_exists_after_migration` — 인덱스 생성 검증
  - `test_0004_order_index_covers_order_index_column` — column_names 확인
  - `test_0004_order_index_is_btree` — btree 타입 확인

### Step 3: Create Migration (Completed)
- `alembic/versions/0004_add_contextitem_order_index.py` 작성
- `upgrade()`: `op.create_index("ix_rag_contextitem_order_index", "rag_contextitem", ["order_index"])`
- `downgrade()`: `op.drop_index("ix_rag_contextitem_order_index", "rag_contextitem")`

### Step 4: Verify Operations (Completed)
- ✅ `alembic upgrade head` → 인덱스 생성 확인
- ✅ `alembic downgrade -1` → 인덱스 삭제 확인
- ✅ `alembic upgrade head` → 재생성 확인
- ✅ 멱등성 테스트: 동일 버전에서 재실행 시 에러 없음
- ✅ 전체 테스트 통과: 197 passed, 83% coverage

## Current Failures
없음

## Decision Log
- **Scope 축소**: 초기 제안 3개 인덱스 → 실제 필요 1개 인덱스로 축소 (research 결과 반영)
- **Manual migration**: `alembic revision` Mako 템플릿 오류로 인해 수동 작성

## Next Step
문서 업데이트 (AGENTS.md에 마이그레이션 가이드 반영) → 커밋
