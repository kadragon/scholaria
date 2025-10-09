Goal: FastAPI 토픽 엔드포인트에서 Django와 동일한 Topic↔Context 관계 노출 확보
Key Changes:
- SQLAlchemy 다대다 조인 테이블 `topic_context_association` 추가 및 Topic/Context 모델 관계 확장
- Pydantic `TopicOut` 스키마에 contexts 리스트 추가, 라우터에서 `selectinload`로 eager 로딩 적용
- pytest 시나리오에 컨텍스트 연결 검증 로직 추가 및 PostgreSQL 컨테이너 활용해 통과 확인
Tests:
- `uv run pytest --override-ini addopts="" api/tests/test_topics_poc.py`
Notes:
- Docker compose 기반 PostgreSQL(포트 5432) 필요, 테스트 DB 종료 시 세션 잔존 경고 존재
