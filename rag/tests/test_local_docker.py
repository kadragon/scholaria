"""Tests for local Docker development configuration."""

from __future__ import annotations

from pathlib import Path

from django.test import SimpleTestCase


class LocalDockerComposeTest(SimpleTestCase):
    """Verify that local Docker compose setup supports app testing."""

    def setUp(self) -> None:
        """Configure commonly used paths."""
        self.project_root = Path(__file__).parent.parent.parent
        self.local_compose = self.project_root / "docker-compose.dev.yml"
        self.dockerfile_dev = self.project_root / "Dockerfile.dev"

    def test_local_docker_files_exist(self) -> None:
        """Local Docker compose and Dockerfile should be present."""
        for file_path in (self.local_compose, self.dockerfile_dev):
            self.assertTrue(
                file_path.exists(),
                f"Expected local Docker artefact missing: {file_path}",
            )

    def test_local_docker_compose_web_service(self) -> None:
        """Local compose file should define a Django web service."""
        self.assertTrue(self.local_compose.exists())
        content = self.local_compose.read_text()

        expected_snippets = [
            "web:",
            "build:",
            "dockerfile: Dockerfile.dev",
            "command: ./scripts/docker/dev-entrypoint.sh",
            "depends_on:",
            "postgres:",
            "redis:",
            "qdrant:",
            "ports:",
            "${WEB_PORT:-8000}:8000",
            "volumes:",
            "- .:/app",
            "environment:",
            "DJANGO_SETTINGS_MODULE: core.settings",
        ]

        for snippet in expected_snippets:
            self.assertIn(
                snippet,
                content,
                f"Local docker-compose.dev.yml missing snippet: {snippet}",
            )
