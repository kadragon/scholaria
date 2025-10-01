Goal: FastAPI `/api/topics` POC가 Django API와 동일한 JSON을 제공하도록 보증
Key Changes:
- SQLAlchemy Topic↔Context 관계 정렬을 ID 기준으로 맞추고 Django와 응답 순서를 동기화
- Pydantic 스키마에 타임존 직렬화(field_serializer) 도입해 `settings.TIME_ZONE` 기준 ISO 문자열 반환
- FastAPI 대 Django 응답 비교 및 메소드 제한 테스트 추가
Tests:
- `uv run pytest --override-ini addopts="" api/tests/test_topics_poc.py`
Notes:
- 테스트 종료 시 PostgreSQL 세션이 잔류해 경고가 발생할 수 있음 (병렬 세션 4개)
