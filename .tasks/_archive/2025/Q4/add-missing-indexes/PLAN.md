# Plan: Add Missing Indexes

## Objective
`rag_contextitem.order_index`에 btree 인덱스 추가하여 정렬 쿼리 성능 향상

## Constraints
- Alembic 마이그레이션만 사용 (SQLAlchemy DDL)
- 기존 데이터 영향 없음 (스키마만 변경)
- up/down 멱등성 보장

## Target Files & Changes

### 1. Migration Script
**File**: `alembic/versions/0004_add_order_index_to_contextitem.py` (새 파일)
- `upgrade()`: `CREATE INDEX ix_rag_contextitem_order_index ON rag_contextitem (order_index)`
- `downgrade()`: `DROP INDEX ix_rag_contextitem_order_index`

### 2. Migration Test
**File**: `backend/tests/test_alembic_migrations.py` (새 파일)
- `test_0004_upgrade_creates_order_index` — 인덱스 생성 검증
- `test_0004_downgrade_drops_order_index` — 인덱스 제거 검증
- `test_0004_idempotent_upgrade` — 중복 실행 안전성

## Test/Validation Cases

### Red Tests (먼저 작성)
1. **인덱스 존재 검증 실패** — 마이그레이션 전 인덱스 부재 확인
2. **업그레이드 후 인덱스 생성** — `ix_rag_contextitem_order_index` 존재
3. **다운그레이드 후 인덱스 제거** — 인덱스 삭제 확인
4. **멱등성** — 동일 마이그레이션 재실행 시 에러 없음

## Steps

- [ ] **Step 1**: Write failing test `test_alembic_migrations.py`
- [ ] **Step 2**: Generate Alembic migration `0004_add_order_index_to_contextitem.py`
- [ ] **Step 3**: Run migration (`alembic upgrade head`)
- [ ] **Step 4**: Verify tests pass (green)
- [ ] **Step 5**: Test downgrade (`alembic downgrade -1`)
- [ ] **Step 6**: Re-upgrade and verify idempotency

## Rollback
```bash
alembic downgrade -1
```
롤백 안전: 인덱스 삭제만 수행하며 데이터 손실 없음.

## Review Hotspots
- Postgres 인덱스 네이밍 규칙 (`ix_<table>_<column>`)
- Alembic `create_index`/`drop_index` if_exists 처리
