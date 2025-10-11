#!/bin/bash
set -euo pipefail

# Bootstrap uv environment if not already present inside the backend project.
PROJECT_DIR=${UV_PROJECT_DIR:-/app/backend}
if [ ! -x "${UV_PROJECT_ENVIRONMENT:-${PROJECT_DIR}/.venv}/bin/python" ]; then
    echo "[fastapi-dev-entrypoint] Bootstrapping uv environment..."
    (cd "${PROJECT_DIR}" && uv sync --dev)
fi

DEFAULT_CMD=(uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001)

if [ "$#" -gt 0 ]; then
    exec "$@"
else
    cd "${PROJECT_DIR}"
    exec "${DEFAULT_CMD[@]}"
fi
