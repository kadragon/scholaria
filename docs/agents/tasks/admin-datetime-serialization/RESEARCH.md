# Research: Admin Datetime Serialization

## Goal
`backend/schemas/admin.py`의 `AdminTopicOut`, `AdminContextOut` 스키마에 ISO 8601 timezone-aware datetime 직렬화 추가

## Scope
- 파일: `backend/schemas/admin.py`
- 타깃 스키마: `AdminTopicOut` (L10-25), `AdminContextOut` (L55-68)
- 적용 필드: `created_at`, `updated_at`

## Related Files & Flows
- **유틸리티**: `backend/schemas/utils.to_local_iso()` — timezone-aware ISO 포맷 변환
- **기존 패턴**: `backend/schemas/context.py:26-28`, `topic.py:32`, `history.py:36` 모두 `@field_serializer` 데코레이터 사용
- **테스트**: `backend/tests/admin/test_admin_topics_read.py`, `test_admin_contexts_read.py` — 응답 필드 검증

## Hypotheses
1. **기존 패턴 재사용**: 다른 스키마(`ContextOut`, `TopicOut`)와 동일한 `@field_serializer` 적용으로 일관성 확보
2. **최소 변경**: 새 필드 추가 없이 직렬화 로직만 추가 (Breaking change 최소화)
3. **테스트 통과**: 기존 테스트는 ISO 문자열 포맷을 허용하므로 추가 수정 불필요 가능성 높음

## Evidence
- AGENTS.md L78-81: 현재 `AdminTopicOut`, `AdminContextOut`은 datetime 직렬화 미적용 상태로 명시
- context.py/topic.py: `@field_serializer("created_at", "updated_at")` + `to_local_iso()` 동일 패턴
- utils.py: `to_local_iso()` 함수 — naive datetime을 UTC로 간주하고 프로젝트 타임존으로 변환

## Assumptions / Open Questions
- ❓ 프론트엔드(Refine Admin)가 ISO 문자열을 올바르게 파싱하는지 확인 필요 (기존 스키마는 이미 적용 중이므로 가능성 높음)
- ✅ Pydantic V2 `@field_serializer` 데코레이터는 `model_dump()` / JSON 직렬화 시 자동 호출

## Risks
- **Breaking change 가능성**: Admin API를 소비하는 클라이언트가 datetime 객체를 기대하는 경우 오류 (현재는 FastAPI가 자동 직렬화하므로 문자열로 전송 중)
- **타임존 혼란**: UTC vs 로컬 타임존 — `utils.py`는 UTC 기본 설정 중 (`_LOCAL_ZONE = ZoneInfo("UTC")`)

## Next
→ **Plan** 단계: TDD 시나리오 작성, 변경 범위 확정, 테스트 전략 수립
