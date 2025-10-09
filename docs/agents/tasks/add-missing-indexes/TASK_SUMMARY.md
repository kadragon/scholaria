# Task Summary: Add Missing Indexes

## Goal
`rag_contextitem.order_index`에 btree 인덱스 추가하여 정렬 쿼리 성능 향상

## Core Changes
- **Migration**: `alembic/versions/0004_add_contextitem_order_index.py` 작성
  - `upgrade()`: `CREATE INDEX ix_rag_contextitem_order_index ON rag_contextitem (order_index)`
  - `downgrade()`: `DROP INDEX ix_rag_contextitem_order_index`
- **Tests**: `backend/tests/test_alembic_migrations.py` 추가 (3개 테스트)
  - 인덱스 존재/컬럼/타입 검증
- **Docs**: `docs/agents/AGENTS.md` Alembic 가이드 추가

## Tests
- ✅ 197 passed, 83% coverage
- ✅ 마이그레이션 up/down/idempotency 검증 완료

## Branch & Commit
- Branch: `chore/add-missing-indexes`
- Files: `alembic/versions/0004_*.py`, `backend/tests/test_alembic_migrations.py`, `docs/agents/AGENTS.md`, `docs/agents/tasks/add-missing-indexes/`
