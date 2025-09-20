import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_pyproject() -> dict:
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as f:
        return tomllib.load(f)


def test_pytest_configuration_enables_parallel_execution() -> None:
    config = load_pyproject()
    dependencies = config["project"]["dependencies"]
    pytest_dependencies = [
        dep for dep in dependencies if dep.startswith("pytest-xdist")
    ]
    assert (
        pytest_dependencies
    ), "Expected pytest-xdist dependency to be declared for parallel testing"

    addopts = config["tool"]["pytest"]["ini_options"]["addopts"]
    parallel_flags = [opt for opt in addopts if opt.startswith("-n")]
    assert (
        parallel_flags
    ), "Expected pytest to enable xdist worker configuration via -n option"
    assert any(
        opt in {"-n=auto", "-n auto"} for opt in parallel_flags
    ), "Expected pytest to default to auto-detected worker count"
