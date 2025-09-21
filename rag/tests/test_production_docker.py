"""Tests for production Docker configuration."""

from __future__ import annotations

import re
from pathlib import Path

from django.test import TestCase


class ProductionDockerTest(TestCase):
    """Test cases to validate production Docker configuration."""

    def setUp(self) -> None:
        """Set up test paths."""
        self.project_root = Path(__file__).parent.parent.parent
        self.docker_compose_prod = self.project_root / "docker-compose.prod.yml"
        self.dockerfile_prod = self.project_root / "Dockerfile.prod"
        self.env_prod_example = self.project_root / ".env.prod.example"
        self.deploy_script = self.project_root / "scripts" / "deploy.sh"
        self.nginx_conf = self.project_root / "nginx" / "nginx.conf"
        self.production_settings = self.project_root / "core" / "production_settings.py"
        self.docker_docs = self.project_root / "docs" / "PRODUCTION_DOCKER.md"

    def test_production_docker_files_exist(self) -> None:
        """Test that all production Docker files exist."""
        required_files = [
            self.docker_compose_prod,
            self.dockerfile_prod,
            self.env_prod_example,
            self.deploy_script,
            self.nginx_conf,
            self.production_settings,
            self.docker_docs,
        ]

        for file_path in required_files:
            self.assertTrue(
                file_path.exists(),
                f"Production Docker file missing: {file_path}",
            )

    def test_docker_compose_prod_services(self) -> None:
        """Test that production Docker Compose contains required services."""
        self.assertTrue(self.docker_compose_prod.exists())
        content = self.docker_compose_prod.read_text()

        required_services = [
            "web:",
            "celery-worker:",
            "celery-beat:",
            "postgres:",
            "redis:",
            "qdrant:",
            "minio:",
            "nginx:",
        ]

        for service in required_services:
            self.assertIn(
                service,
                content,
                f"Production Docker Compose missing service: {service}",
            )

    def test_docker_compose_prod_security_features(self) -> None:
        """Test that production Docker Compose includes security configurations."""
        self.assertTrue(self.docker_compose_prod.exists())
        content = self.docker_compose_prod.read_text()

        security_features = [
            "restart: unless-stopped",
            "healthcheck:",
            "deploy:",
            "resources:",
            "networks:",
            "scholaria-network",
        ]

        for feature in security_features:
            self.assertIn(
                feature,
                content,
                f"Production Docker Compose missing security feature: {feature}",
            )

    def test_dockerfile_prod_multi_stage(self) -> None:
        """Test that production Dockerfile uses multi-stage build."""
        self.assertTrue(self.dockerfile_prod.exists())
        content = self.dockerfile_prod.read_text()

        dockerfile_features = [
            "FROM python:3.13-slim as builder",
            "FROM python:3.13-slim as production",
            "COPY --from=builder",
            "USER scholaria",
            "HEALTHCHECK",
        ]

        for feature in dockerfile_features:
            self.assertIn(
                feature,
                content,
                f"Production Dockerfile missing feature: {feature}",
            )

    def test_env_prod_example_required_vars(self) -> None:
        """Test that production environment example includes required variables."""
        self.assertTrue(self.env_prod_example.exists())
        content = self.env_prod_example.read_text()

        required_vars = [
            "SECRET_KEY=",
            "ALLOWED_HOSTS=",
            "POSTGRES_DB=",
            "POSTGRES_USER=",
            "POSTGRES_PASSWORD=",
            "OPENAI_API_KEY=",
            "MINIO_ACCESS_KEY=",
            "MINIO_SECRET_KEY=",
        ]

        for var in required_vars:
            self.assertIn(
                var,
                content,
                f"Production environment example missing variable: {var}",
            )

    def test_deploy_script_executable_and_functions(self) -> None:
        """Test that deploy script is executable and contains required functions."""
        self.assertTrue(self.deploy_script.exists())
        content = self.deploy_script.read_text()

        script_functions = [
            "deploy()",
            "update()",
            "backup()",
            "health()",
            "check_prerequisites()",
        ]

        for function in script_functions:
            self.assertIn(
                function,
                content,
                f"Deploy script missing function: {function}",
            )

        # Check that script has shebang
        self.assertTrue(
            content.startswith("#!/bin/bash"),
            "Deploy script should start with #!/bin/bash",
        )

    def test_nginx_conf_security_headers(self) -> None:
        """Test that Nginx configuration includes security headers."""
        self.assertTrue(self.nginx_conf.exists())
        content = self.nginx_conf.read_text()

        security_headers = [
            "add_header X-Frame-Options",
            "add_header X-Content-Type-Options",
            "add_header X-XSS-Protection",
            "add_header Referrer-Policy",
            "add_header Content-Security-Policy",
        ]

        for header in security_headers:
            self.assertIn(
                header,
                content,
                f"Nginx configuration missing security header: {header}",
            )

    def test_nginx_conf_rate_limiting(self) -> None:
        """Test that Nginx configuration includes rate limiting."""
        self.assertTrue(self.nginx_conf.exists())
        content = self.nginx_conf.read_text()

        rate_limiting_features = [
            "limit_req_zone",
            "limit_req zone=api",
            "limit_req zone=login",
        ]

        for feature in rate_limiting_features:
            self.assertIn(
                feature,
                content,
                f"Nginx configuration missing rate limiting: {feature}",
            )

    def test_production_settings_security(self) -> None:
        """Test that production settings include security configurations."""
        self.assertTrue(self.production_settings.exists())
        content = self.production_settings.read_text()

        security_settings = [
            "DEBUG = False",
            "SECURE_BROWSER_XSS_FILTER = True",
            "SECURE_CONTENT_TYPE_NOSNIFF = True",
            'X_FRAME_OPTIONS = "DENY"',
            "SESSION_COOKIE_SECURE",
            "CSRF_COOKIE_SECURE",
        ]

        for setting in security_settings:
            self.assertIn(
                setting,
                content,
                f"Production settings missing security config: {setting}",
            )

    def test_production_docker_documentation(self) -> None:
        """Test that production Docker documentation is comprehensive."""
        self.assertTrue(self.docker_docs.exists())
        content = self.docker_docs.read_text().lower()

        required_sections = [
            "# production docker deployment guide",
            "## architecture overview",
            "## quick start",
            "## security features",
            "## performance optimizations",
            "## monitoring & health checks",
            "## backup & recovery",
            "## ssl/https configuration",
        ]

        for section in required_sections:
            self.assertRegex(
                content,
                rf"(?m)^\s*{re.escape(section)}\s*$",
                f"Production Docker docs missing section: {section}",
            )

    def test_health_check_endpoint_configured(self) -> None:
        """Test that health check endpoint is properly configured."""
        # Check that health check URL is in main URLs
        main_urls = self.project_root / "core" / "urls.py"
        self.assertTrue(main_urls.exists())
        main_urls_content = main_urls.read_text()

        self.assertIn(
            'path("health/", HealthCheckView.as_view(), name="health-check")',
            main_urls_content,
            "Health check endpoint not configured in main URLs",
        )

        # Check that HealthCheckView is imported
        self.assertIn(
            "from rag.views import HealthCheckView",
            main_urls_content,
            "HealthCheckView not imported in main URLs",
        )
