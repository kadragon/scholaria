# Docker Integration - Agent Knowledge Base

## Intent
`docker compose` 스택으로 Scholaria RAG 서비스를 통합 테스트/운영한다.

## Constraints
- **TDD Methodology**: Red → Green → Refactor 사이클을 유지한다.
- **Environment Isolation**: 통합 테스트 시 `DOCKER_INTEGRATION_TESTS=true`로 외부 연동을 구분한다.
- **Performance**: 백엔드(8001), Qdrant(6333), PostgreSQL(5432), Redis(6379), 프론트엔드(5173)가 정상 응답해야 한다.
- **Graceful Degradation**: 개별 서비스 장애 시 명확한 에러 메시지와 롤백 전략을 제공한다.

## Context

### Services
- `backend`: FastAPI, `Dockerfile.backend`의 `development` 스테이지 + `scripts/docker/dev-entrypoint.sh`.
- `postgres`, `redis`, `qdrant`: 데이터 계층.
- `frontend`: Refine/Vite dev server (Node 20 Alpine, 포트 5173).
- `celery-worker`, `flower`: 비동기 작업 및 모니터링.
- 프로덕션 구성(`docker-compose.prod.yml`)은 nginx 리버스 프록시를 추가한다.

### Development Setup
- 단일 `docker-compose.yml`로 로컬 개발 및 통합 테스트를 수행한다.
- 시작: `docker compose up -d` / 종료: `docker compose down -v`.
- 마이그레이션 및 관리 작업은 `docker compose exec backend uv run alembic upgrade head` 패턴을 따른다.
- 프론트엔드 노드 패키지는 볼륨으로 마운트되며 최초 실행 시 자동 설치된다.

### Test Coverage
- 통합 테스트는 `uv run pytest backend/tests/`에서 Redis/Qdrant/PostgreSQL 의존성을 요구하는 케이스를 포함한다.
- Docker 환경에서 실행할 때는 `DOCKER_INTEGRATION_TESTS=true`로 외부 서비스 연동을 활성화하고, 서비스 헬스체크를 통과해야 한다.
- 성능 기준: Redis 핑 < 1s, Qdrant 검색 < 2s, PostgreSQL 연결 즉시 완료.

## Changelog

### 2025-10-09
- 개발용 오버레이(`docker-compose.dev.yml`) 제거, 단일 compose 파일로 정리.
- 서비스 목록을 backend/postgres/redis/qdrant/frontend/celery-worker/flower로 업데이트.
- 프로덕션 nginx 구성을 `docker-compose.prod.yml` 섹션에 반영.
