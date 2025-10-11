#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}/backend"

declare -a ARGS=()
for path in "$@"; do
  if [[ "${path}" == backend/* ]]; then
    ARGS+=("${path#backend/}")
  else
    ARGS+=("${path}")
  fi
done

if [[ ${#ARGS[@]} -eq 0 ]]; then
  uv run mypy
else
  uv run mypy "${ARGS[@]}"
fi
