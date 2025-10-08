# Plan: Admin Datetime Serialization

## Objective
`AdminTopicOut`, `AdminContextOut` 스키마에 `created_at`, `updated_at` 필드 ISO 8601 직렬화 추가하여 기존 스키마(`ContextOut`, `TopicOut`)와 동일한 패턴 적용

## Constraints
- **TDD 필수**: Red → Green → Refactor
- **기존 패턴 재사용**: `@field_serializer` + `to_local_iso()` (context.py/topic.py 동일 구조)
- **테스트 통과**: 기존 관리자 API 테스트 134개 유지

## Target Files & Changes

### 1. `backend/schemas/admin.py`
- **AdminTopicOut** (L10-25)
  - `from pydantic import field_serializer` import 추가
  - `from backend.schemas.utils import to_local_iso` import 추가
  - L25 이후 `@field_serializer("created_at", "updated_at")` 메서드 추가
- **AdminContextOut** (L55-68)
  - L68 이후 동일한 serializer 메서드 추가

### 2. `backend/tests/admin/test_admin_topics_read.py`
- 새 테스트: `test_admin_topic_out_datetime_serialization_format`
  - `created_at`, `updated_at`이 ISO 8601 문자열인지 검증
  - 타임존(`+00:00` 또는 `Z`) 포함 여부 확인

### 3. `backend/tests/admin/test_admin_contexts_read.py`
- 새 테스트: `test_admin_context_out_datetime_serialization_format`
  - 동일한 검증 패턴

## Test / Validation Cases

### Red Phase (실패 테스트 작성)
1. **ISO 문자열 포맷**: `created_at`이 `YYYY-MM-DDTHH:MM:SS±TZ` 패턴인지
2. **타임존 포함**: `+00:00` 또는 `Z` 서픽스 존재 확인
3. **역직렬화 가능**: `datetime.fromisoformat()` 파싱 성공

### Green Phase (구현)
1. `AdminTopicOut`에 `@field_serializer` 추가
2. `AdminContextOut`에 동일 메서드 추가

### Refactor Phase
- 중복 제거 필요 시 Base 클래스 고려 (현재는 2개 스키마만이므로 보류)

## Steps

1. [ ] **Red**: 테스트 작성 — `test_admin_topics_read.py`에 datetime 직렬화 검증 테스트 추가 (실패 확인)
2. [ ] **Green**: `AdminTopicOut`에 `@field_serializer` 구현 (테스트 통과)
3. [ ] **Red**: 테스트 작성 — `test_admin_contexts_read.py`에 동일 테스트 추가 (실패 확인)
4. [ ] **Green**: `AdminContextOut`에 `@field_serializer` 구현 (테스트 통과)
5. [ ] **Validate**: 전체 테스트 스위트 실행 (`uv run pytest`)
6. [ ] **Lint**: `uv run ruff check . && uv run mypy .`

## Rollback
- Git revert: `git revert HEAD` (커밋 전 실패 시 `git checkout .`)
- 영향 범위: Admin API 스키마만 (DB/모델 변경 없음)

## Review Hotspots
- **Pydantic serializer**: `@field_serializer` 데코레이터 호출 순서 (Pydantic V2 호환)
- **타임존 일관성**: `_LOCAL_ZONE = ZoneInfo("UTC")` 설정 확인
- **기존 테스트 영향**: Admin API 통합 테스트가 ISO 문자열 수용 여부

## Status
- [ ] Step 1: Red test for AdminTopicOut
- [ ] Step 2: Green implementation for AdminTopicOut
- [ ] Step 3: Red test for AdminContextOut
- [ ] Step 4: Green implementation for AdminContextOut
- [ ] Step 5: Full test suite validation
- [ ] Step 6: Lint & type check
