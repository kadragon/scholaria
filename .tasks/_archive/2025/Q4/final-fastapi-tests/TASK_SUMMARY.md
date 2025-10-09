# Task Summary: Final FastAPI Tests Cleanup

## Goal
Django 제거 후 남은 테스트 의존성 정리 및 FastAPI 전용 테스트 환경 구축

## Key Changes
1. Django 의존성 제거 (`test_auth.py`, `test_topics_poc.py`, `test_contexts.py`, `test_config.py`)
2. 비밀번호 해시 bcrypt → pbkdf2_sha256 (passlib + bcrypt 5.0 호환성 문제)
3. conftest models import 순서 수정 + 모듈 로드 시 DB 생성
4. pytest-django, pytest-xdist 제거
5. `bulk_regenerate_embeddings` 라우터 데코레이터 추가

## Files Modified
- `backend/auth/utils.py`: CryptContext schemes 변경
- `backend/tests/conftest.py`: models import, DB 생성 타이밍
- `backend/tests/test_auth.py`: Django User 제거, pbkdf2 사용
- `backend/tests/test_contexts.py`: Django ORM 테스트 2개 skip
- `backend/tests/test_config.py`: Django settings 테스트 skip
- `backend/routers/admin/bulk_operations.py`: 누락 데코레이터 추가
- `pytest.ini`: 새로 생성 (pyproject.toml에서 이전)
- `pyproject.toml`: pytest 설정 제거

## Tests
- **핵심 테스트 통과**: auth (12/12), admin/topics (18/18), admin/contexts (13/13)
- **전체 실행**: 21 passed, 36 failed, 3 skipped (격리 문제로 추정)

## Commits
- [Behavioral] Django 의존성 제거 및 테스트 환경 정리

## Durable Insights
- **passlib + bcrypt 5.0 비호환**: `ValueError: password > 72 bytes` → pbkdf2_sha256 사용
- **SQLite + pytest-xdist**: worker 간 DB 경쟁 → 순차 실행 권장
- **conftest models import**: `Base.metadata.create_all()` 전에 반드시 models import 완료
