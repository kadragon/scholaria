#!/bin/bash
set -euo pipefail

# Celery worker entrypoint that manages an isolated uv environment outside the bind mount.
PROJECT_DIR=${UV_PROJECT_DIR:-/app/backend}
PROJECT_ENV=${UV_PROJECT_ENVIRONMENT:-/tmp/uv/backend-worker}
UV_BIN_DIR=${CELERY_UV_BIN_DIR:-/tmp/uv-bin}
UV_CONFIG_DIR=${CELERY_UV_CONFIG_DIR:-/tmp/uv-config}
UV_CACHE_DIR=${CELERY_UV_CACHE_DIR:-/tmp/uv-cache}
UV_HOME_DIR=${CELERY_UV_HOME_DIR:-/tmp/uv-home}
UV_PYTHON_VERSION=${UV_PYTHON_VERSION:-3.13}

mkdir -p "${PROJECT_ENV}" "${UV_BIN_DIR}" "${UV_CONFIG_DIR}" "${UV_CACHE_DIR}" "${UV_HOME_DIR}"

export XDG_BIN_HOME="${UV_BIN_DIR}"
export XDG_CONFIG_HOME="${UV_CONFIG_DIR}"
export XDG_CACHE_HOME="${UV_CACHE_DIR}"
export UV_NO_MODIFY_PATH=1
export HOME="${UV_HOME_DIR}"

export PATH="${UV_BIN_DIR}:${PATH}"

if ! command -v uv >/dev/null 2>&1; then
    echo "[celery-entrypoint] Installing uv to ${UV_BIN_DIR}..."
    if ! curl -LsSf https://astral.sh/uv/install.sh | sh; then
        echo "[celery-entrypoint] Failed to install uv" >&2
        exit 1
    fi
fi

export PATH="${PROJECT_ENV}/bin:${PATH}"

cd "${PROJECT_DIR}"

export PYTHONPATH="/app:${PYTHONPATH:-}"

if [ ! -x "${PROJECT_ENV}/bin/python3" ]; then
    echo "[celery-entrypoint] Bootstrapping uv environment at ${PROJECT_ENV}..."
    UV_PROJECT_DIR="${PROJECT_DIR}" UV_PROJECT_ENVIRONMENT="${PROJECT_ENV}" uv sync --frozen --python "${UV_PYTHON_VERSION}"
fi

export UV_PROJECT_DIR="${PROJECT_DIR}"
export UV_PROJECT_ENVIRONMENT="${PROJECT_ENV}"

if [ "$#" -gt 0 ]; then
    exec uv run "$@"
else
    exec uv run celery -A celery_app worker --loglevel="${CELERY_LOGLEVEL:-info}"
fi
