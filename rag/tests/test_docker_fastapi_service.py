"""Tests ensuring FastAPI service is defined in Docker Compose for development."""

from pathlib import Path

import yaml


def test_dev_compose_defines_fastapi_service() -> None:
    """FastAPI service should exist with expected configuration."""
    compose_path = Path(__file__).resolve().parents[2] / "docker-compose.dev.yml"
    assert compose_path.exists(), "docker-compose.dev.yml must exist at project root"

    compose_data = yaml.safe_load(compose_path.read_text())
    services = compose_data.get("services", {})

    assert (
        "fastapi" in services
    ), "FastAPI service is missing from docker-compose.dev.yml"
    fastapi_service = services["fastapi"]

    build_config = fastapi_service.get("build", {})
    assert (
        build_config.get("context") == "."
    ), "FastAPI service should build from project root"
    assert (
        build_config.get("dockerfile") == "Dockerfile.dev"
    ), "FastAPI service should reuse the development Dockerfile"

    command = fastapi_service.get("command")
    assert (
        command == "./scripts/docker/fastapi-dev-entrypoint.sh"
    ), "FastAPI service should boot via dedicated entrypoint for uvicorn"

    ports = fastapi_service.get("ports", [])
    assert (
        "${FASTAPI_PORT:-8001}:8001" in ports
    ), "FastAPI service must expose port 8001"

    environment = fastapi_service.get("environment", {})
    for key in ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"):
        assert key in environment, f"FastAPI service missing {key} environment variable"

    depends_on = fastapi_service.get("depends_on", {})
    for service in ("postgres", "redis", "qdrant"):
        assert service in depends_on, f"FastAPI service should depend on {service}"
