"""Tests for production Docker & Nginx integration (Phase 6.3)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROD_COMPOSE = PROJECT_ROOT / "docker-compose.prod.yml"
NGINX_CONFIG = PROJECT_ROOT / "nginx" / "nginx.conf"


def _load_prod_compose() -> dict[str, Any]:
    assert PROD_COMPOSE.exists(), "docker-compose.prod.yml must exist"
    content = yaml.safe_load(PROD_COMPOSE.read_text())
    assert isinstance(
        content, dict
    ), "docker-compose.prod.yml must be a valid YAML dict"
    return content


def test_prod_compose_defines_fastapi_service() -> None:
    """FastAPI should run as a dedicated service in production compose."""
    compose = _load_prod_compose()
    services = compose.get("services", {})
    assert "fastapi" in services, "fastapi service missing from production compose"

    fastapi_service = services["fastapi"]
    build = fastapi_service.get("build", {})
    assert build.get("context") == ".", "fastapi build context should be project root"
    assert (
        build.get("dockerfile") == "Dockerfile.prod"
    ), "fastapi service should reuse Dockerfile.prod"

    command = fastapi_service.get("command")
    assert command, "fastapi service must define command"
    assert (
        "uvicorn" in command
        if isinstance(command, str)
        else "uvicorn" in " ".join(command)
    )

    expose = fastapi_service.get("expose", [])
    assert "8001" in expose, "fastapi service must expose port 8001 internally"

    environment = fastapi_service.get("environment", [])
    required_env = {
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
        "REDIS_URL",
    }
    if isinstance(environment, list):
        env_keys = {item.split("=")[0] for item in environment}
    elif isinstance(environment, dict):
        env_keys = set(environment.keys())
    else:
        env_keys = set()
    missing = required_env - env_keys
    assert not missing, f"fastapi service missing env vars: {sorted(missing)}"

    depends_on = fastapi_service.get("depends_on", {})
    for dependency in ("postgres", "redis", "qdrant"):
        assert (
            dependency in depends_on
        ), f"fastapi service should depend on {dependency} in production compose"


def test_prod_compose_defines_admin_frontend_service() -> None:
    """Admin frontend SPA should be built and served via dedicated image."""
    compose = _load_prod_compose()
    services = compose.get("services", {})
    assert (
        "admin-frontend" in services
    ), "admin-frontend service missing from production compose"

    admin_service = services["admin-frontend"]
    build = admin_service.get("build", {})
    assert (
        build.get("context") == "."
    ), "admin-frontend build context should be project root"
    assert (
        build.get("dockerfile") == "Dockerfile.admin"
    ), "admin-frontend should use Dockerfile.admin"

    expose = admin_service.get("expose", [])
    assert "8080" in expose or "80" in expose, "admin-frontend should expose HTTP port"


def test_nginx_config_routes_fastapi_and_admin() -> None:
    """Main nginx proxy should route /api and /admin appropriately."""
    assert NGINX_CONFIG.exists(), "nginx/nginx.conf must exist"
    config_text = NGINX_CONFIG.read_text()

    assert "upstream fastapi" in config_text, "nginx config missing fastapi upstream"
    assert (
        "server fastapi:8001" in config_text
    ), "fastapi upstream must point to service port"
    assert (
        "upstream admin_frontend" in config_text
    ), "nginx config missing admin_frontend upstream"

    api_block = re.search(r"location /api/? ?\{(?P<body>.*?)\}", config_text, re.DOTALL)
    assert api_block, "nginx config missing /api location block"
    assert "proxy_pass http://fastapi;" in api_block.group(
        "body"
    ), "/api block should proxy to fastapi upstream"

    docs_block = re.search(
        r"location /docs/? ?\{(?P<body>.*?)\}", config_text, re.DOTALL
    )
    assert docs_block, "nginx config should expose FastAPI docs"
    assert "proxy_pass http://fastapi;" in docs_block.group(
        "body"
    ), "/docs block should proxy to fastapi upstream"

    admin_block = re.search(
        r"location /admin/? ?\{(?P<body>.*?)\}", config_text, re.DOTALL
    )
    assert admin_block, "nginx config missing /admin block"
    admin_body = admin_block.group("body")
    assert (
        "proxy_pass http://admin_frontend/;" in admin_body
    ), "/admin block should proxy to admin frontend"
    assert (
        "proxy_redirect off;" in admin_body
    ), "/admin block should disable proxy redirects"

    redirect_block = re.search(
        r"location /admin \{(?P<body>.*?)\}", config_text, re.DOTALL
    )
    assert redirect_block, "nginx config should redirect /admin to /admin/"
    assert "return 301 /admin/;" in redirect_block.group(
        "body"
    ), "/admin redirect block must enforce trailing slash"
