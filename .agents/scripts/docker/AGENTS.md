# Scripts/Docker - Agent Knowledge Base

## Intent
컨테이너 엔트리포인트가 로컬 개발 환경을 안전하게 부트스트랩하도록 문서화한다.

## Constraints
- POSIX 셸만 사용하며 macOS/Linux Docker Desktop 양쪽에서 동일하게 동작해야 한다.
- 볼륨 마운트로 이미지를 덮어써도 멱등하게 재실행되어야 한다.
- uv 명령은 비대화형으로 실행하고 실패 시 즉시 종료한다.

## Context
- `scripts/docker/dev-entrypoint.sh`
  - `/opt/uv` (또는 `$UV_PROJECT_ENVIRONMENT`) 아래 Python 실행 파일이 없으면 `uv sync --dev`로 의존성을 재설치한다.
  - 기본 커맨드는 `uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001`.
  - 추가 인자가 전달되면 그대로 실행하여 커스텀 명령을 지원한다.
- 백엔드 컨테이너는 `docker-compose.yml`에서 이 엔트리포인트를 사용해 핫 리로드 개발 서버를 기동한다.

## Changelog

### 2025-10-09
- uv 환경 복구 동작(`uv sync --dev`)과 인자 전달 방식을 문서에 반영했다.
