# Research: Django Remnant Audit

## Goal
FastAPI 전용 구성으로 전환된 후 프로젝트에 Django 관련 잔재물(설정, 의존성, 환경변수, 코드 참조)이 남아있는지 감사하고 제거 또는 FastAPI 등가물로 치환한다.

## Scope
- **Configuration files**: `.env`, `docker-compose.yml`, `pyproject.toml`, `alembic.ini` 등
- **Source code**: `backend/`, `scripts/`, `frontend/` 내 Django 참조
- **Dependencies**: `pyproject.toml`, `uv.lock` 내 Django 패키지
- **Documentation**: README, deployment guides, architecture docs
- **Test fixtures**: pytest 구성, conftest.py

## Related Files
- `pyproject.toml` - 의존성 정의
- `uv.lock` - 잠금 파일
- `backend/**/*.py` - 소스 코드
- `scripts/**/*` - 스크립트
- `docker-compose*.yml` - Docker 구성
- `.env.example`, `.env.prod.example` - 환경변수 템플릿
- `docs/**/*.md` - 문서
- `backend/tests/conftest.py` - 테스트 픽스처

## Hypotheses
1. `pyproject.toml`에 Django 관련 의존성이 남아있을 수 있음 (django, django-*, pytest-django 등)
2. 환경변수 파일에 DJANGO_* 또는 Django 전용 설정이 남아있을 수 있음
3. 코드베이스에 `django.` import나 `sync_to_async` 같은 Django ORM 호환 코드가 남아있을 수 있음
4. Docker Compose에 Django 관련 서비스나 환경변수가 남아있을 수 있음
5. 문서에 Django 참조가 남아있을 수 있음

## Evidence

### ✅ Clean (Django 잔재물 없음)
1. **pyproject.toml**: Django 의존성 완전히 제거됨 (django, pytest-django 등 없음)
2. **uv.lock**: Django 관련 패키지 검색 결과 없음
3. **환경변수**: `.env.example`에 DJANGO_ 접두사 없음, FastAPI 중심 구성
4. **Docker Compose**: Django 서비스 없음, 기본 인프라만 존재 (postgres, redis, qdrant)
5. **pytest.ini**: pytest-django 플러그인 참조 없음, 순수 pytest 구성
6. **conftest.py**: Django fixture 없음, FastAPI TestClient + SQLAlchemy 기반

### ⚠️ Requires Attention
1. **asgiref.sync.sync_to_async** 사용:
   - `backend/services/rag_service.py:114-137`에서 4회 사용
   - Django ORM 호환을 위해 도입되었으나 FastAPI에서는 불필요
   - asgiref는 pyproject.toml 명시적 의존성에 없음 (타 패키지의 전이 의존성으로 추정)
   - FastAPI native async 패턴으로 전환 가능

### 📋 Documentation Review Pending
- README.md, DEPLOYMENT.md, ARCHITECTURE_DECISIONS.md 등 문서 내 Django 참조 여부 미확인

## Assumptions
- Phase 8 (Django 제거)가 완료되었다고 표시되어 있으나, 세부적인 잔재물 감사는 수행되지 않았을 수 있음
- 일부 Django 호환 패턴(예: bcrypt → pbkdf2_sha256)이 전환되었으나 완전성을 검증할 필요가 있음

## Open Questions
- Celery와 같은 비동기 인프라가 Django에 특화되어 있었는지? (백로그 태스크 존재)
- pytest 구성에서 Django 관련 플러그인이 완전히 제거되었는지?

## Risks
- Low: 주로 정리 작업이므로 기능적 리스크는 낮음
- Medium: 환경변수나 설정 변경 시 Docker 환경에서 런타임 오류 가능성

## Next
Plan 단계로 진행하여 구체적인 탐색 계획 수립
