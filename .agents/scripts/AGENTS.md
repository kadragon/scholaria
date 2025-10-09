# Scripts Folder - Agent Knowledge Base

## Intent
Scholaria 워크플로우를 자동화하는 POSIX 호환 스크립트를 제공한다.

## Constraints
- POSIX 셸 호환을 유지하고 macOS/Linux에서 동일하게 동작해야 한다.
- 로깅은 기존 이모지 프리픽스(`🐳`, `[INFO]` 등)를 유지해 실행 흐름을 명확히 전달한다.
- 외부 의존성(Docker, uv)이 없으면 즉시 실패하고 해결 방법을 안내한다.
- 현재 서비스 토폴로지(backend, postgres, redis, qdrant, frontend, celery-worker, flower)에 맞춰 헬스체크와 경고 메시지를 갱신한다.

## Context
- `scripts/test_docker_integration.sh`
  - `docker compose`가 우선이며, 미지원 환경에서는 `docker-compose` 바이너리로 자동 폴백한다.
  - 필수 서비스(postgres, redis, qdrant)의 헬스체크가 통과할 때까지 대기하고, 선택 서비스(frontend, flower, celery-worker)는 상태만 보고한다.
  - `uv run alembic upgrade head` 후 `uv run pytest backend/tests/test_rag_endpoint.py backend/tests/test_rag_streaming.py -v --tb=short`를 실행한다.
  - 종료 시 자동으로 컨테이너를 내리지 않으므로 사용자가 `${COMPOSE_CMD[*]} down`으로 정리해야 한다.
- `scripts/docker/dev-entrypoint.sh`
  - uv 환경(`/opt/uv`)이 손실된 경우 `uv sync --dev`로 재구축 후 `uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001`을 실행한다.

## Changelog

### 2025-10-09
- 통합 테스트 스크립트가 `docker compose`/`docker-compose` 양쪽을 지원하고 최신 RAG 테스트 경로를 실행하도록 갱신했다.
- 선택 서비스 안내 메시지를 Qdrant/Flower/Frontend 중심으로 재정리했다.
