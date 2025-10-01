#!/bin/bash
set -euo pipefail

# Ensure development dependencies are installed inside the container-specific environment.
if [ ! -x "${UV_PROJECT_ENVIRONMENT:-/opt/uv}/bin/python" ]; then
    echo "[dev-entrypoint] Bootstrapping uv environment..."
    uv sync --dev
fi

DEFAULT_CMD=(uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001)

if [ "$#" -gt 0 ]; then
    exec "$@"
else
    exec "${DEFAULT_CMD[@]}"
fi
