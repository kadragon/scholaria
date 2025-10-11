"""Regression tests ensuring Django code is not reintroduced into backend runtime."""

from __future__ import annotations

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RUNTIME_DIRS = [
    PROJECT_ROOT / "backend",
]


@pytest.mark.parametrize("target_dir", RUNTIME_DIRS)
def test_backend_contains_no_django_imports(target_dir: Path) -> None:
    """Fail if any backend module still imports Django."""
    offenders: list[tuple[Path, str]] = []
    for path in target_dir.rglob("*.py"):
        # Skip compiled artifacts or migration stubs if present
        if path.name.endswith(".pyc"):
            continue
        if ".venv" in path.parts:
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("from django") or stripped.startswith(
                "import django"
            ):
                offenders.append((path.relative_to(target_dir), stripped))
    assert not offenders, f"Django imports detected: {offenders}"
