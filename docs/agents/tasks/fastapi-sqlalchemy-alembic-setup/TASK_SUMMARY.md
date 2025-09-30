Goal: FastAPI SQLAlchemy 모델용 Alembic 초기 설정을 완료해 Django와 병행 운영 기반 마련
Key Changes:
- `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`, `alembic/versions/0001_baseline.py` 추가로 Alembic 스크립트 디렉터리 구성
- `api/tests/test_alembic_setup.py` 도입(설정 파일 존재, metadata에 `rag_topic` 포함 확인)
- `api/schemas/utils.py`에 타임존 직렬화 유틸 추가 및 스키마에서 field_serializer 사용
Tests:
- `uv run pytest --override-ini addopts="" api/tests/test_alembic_setup.py`
- `uv run pytest --override-ini addopts="" api/tests/test_topics_poc.py`
Notes:
- Alembic env는 기본적으로 실행되지 않도록 `config.cmd_opts` 존재 시에만 마이그레이션 실행
- 테스트 종료 시 PostgreSQL 세션 잔류 경고가 발생할 수 있음
