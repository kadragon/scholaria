#!/bin/bash
set -euo pipefail

# Bootstrap uv environment if not already present inside the container.
if [ ! -x "${UV_PROJECT_ENVIRONMENT:-/opt/uv}/bin/python" ]; then
    echo "[fastapi-dev-entrypoint] Bootstrapping uv environment..."
    uv sync --dev
fi

DEFAULT_CMD=(uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8001)

if [ "$#" -gt 0 ]; then
    exec "$@"
else
    exec "${DEFAULT_CMD[@]}"
fi
