# Task Summary: Admin Datetime Serialization

## Objective
Admin API 스키마 `AdminTopicOut`, `AdminContextOut`의 `created_at`, `updated_at` 필드에 ISO 8601 timezone-aware 직렬화 적용 + DRY 리팩터링

## Key Changes
- **backend/schemas/admin.py**: `AdminBaseOut` 기본 클래스 도입 (공통 필드 + datetime serializer)
- **backend/schemas/admin.py**: `AdminTopicOut`, `AdminContextOut` 상속 변경 (중복 25줄 → 공통 기반 클래스)
- **backend/tests/admin/test_admin_topics.py**: `TestTopicsDatetimeSerialization` 클래스 추가 (1 테스트)
- **backend/tests/admin/test_admin_contexts.py**: `TestContextsDatetimeSerialization` 클래스 추가 (1 테스트)
- **docs/agents/AGENTS.md**: Pydantic 스키마 패턴 업데이트 (datetime 직렬화 적용 완료 목록)

## Tests
- ✅ Red-Green-Refactor TDD 사이클 완료
- ✅ 전체 테스트 스위트 195 passed (리팩터링 후 재검증)
- ✅ ruff + mypy 통과

## Commits
- `0e200af` [Behavioral] feat(admin): Add ISO 8601 datetime serialization
- `292b01b` [Structural] docs: Update TASKS.md with completed datetime serialization
- `70b085e` [Structural] refactor(admin): Extract AdminBaseOut for common fields

## References
- Task slug: `admin-datetime-serialization`
- Branch: `feat/admin-datetime-serialization`
- Files: backend/schemas/admin.py:12-25 (AdminBaseOut), 28-36 (AdminTopicOut), 65-69 (AdminContextOut)
