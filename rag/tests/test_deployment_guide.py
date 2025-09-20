"""Tests for deployment guide documentation."""

from __future__ import annotations

import re
from pathlib import Path

from django.test import TestCase


class DeploymentGuideTest(TestCase):
    """Test cases to validate deployment guide documentation."""

    def setUp(self) -> None:
        """Set up test paths."""
        self.project_root = Path(__file__).parent.parent.parent
        self.deployment_guide_path = self.project_root / "docs" / "DEPLOYMENT.md"

    def test_deployment_guide_exists(self) -> None:
        """Test that deployment guide file exists."""
        self.assertTrue(
            self.deployment_guide_path.exists(),
            f"Deployment guide not found at {self.deployment_guide_path}",
        )

    def test_deployment_guide_has_content(self) -> None:
        """Test that deployment guide has substantial content."""
        self.assertTrue(self.deployment_guide_path.exists())
        content = self.deployment_guide_path.read_text()

        # Should have substantial content (at least 1000 characters)
        self.assertGreater(
            len(content), 1000, "Deployment guide should have substantial content"
        )

    def test_deployment_guide_has_required_sections(self) -> None:
        """Test that deployment guide contains all required sections."""
        self.assertTrue(self.deployment_guide_path.exists())
        content = self.deployment_guide_path.read_text().lower()

        required_sections = [
            "# deployment guide",
            "## prerequisites",
            "## quick start",
            "## production setup",
            "## environment variables",
            "## docker compose",
            "## database setup",
            "## security",
            "## monitoring",
            "## troubleshooting",
        ]

        for section in required_sections:
            self.assertRegex(
                content,
                rf"(?m)^\s*{re.escape(section)}\s*$",
                f"Deployment guide missing required section: {section}",
            )

    def test_deployment_guide_contains_environment_variables(self) -> None:
        """Test that deployment guide documents important environment variables."""
        self.assertTrue(self.deployment_guide_path.exists())
        content = self.deployment_guide_path.read_text()

        # Key environment variables that should be documented
        env_vars = [
            "OPENAI_API_KEY",
            "DB_PASSWORD",
            "REDIS_URL",
            "QDRANT_HOST",
            "MINIO_ACCESS_KEY",
            "MINIO_SECRET_KEY",
            "DEBUG",
            "SECRET_KEY",
        ]

        for env_var in env_vars:
            self.assertIn(
                env_var,
                content,
                f"Deployment guide should document {env_var} environment variable",
            )

    def test_deployment_guide_contains_docker_commands(self) -> None:
        """Test that deployment guide contains Docker commands."""
        self.assertTrue(self.deployment_guide_path.exists())
        content = self.deployment_guide_path.read_text()

        docker_commands = [
            "docker-compose up",
            "docker-compose down",
            "docker-compose logs",
        ]

        for command in docker_commands:
            self.assertIn(
                command, content, f"Deployment guide should contain {command} command"
            )

    def test_deployment_guide_contains_migration_instructions(self) -> None:
        """Test that deployment guide contains database migration instructions."""
        self.assertTrue(self.deployment_guide_path.exists())
        content = self.deployment_guide_path.read_text()

        migration_terms = ["migrate", "makemigrations", "createsuperuser"]

        for term in migration_terms:
            self.assertIn(term, content, f"Deployment guide should mention {term}")

    def test_deployment_guide_has_security_section(self) -> None:
        """Test that deployment guide has security considerations."""
        self.assertTrue(self.deployment_guide_path.exists())
        content = self.deployment_guide_path.read_text().lower()

        security_topics = ["secret_key", "password", "security", "https", "ssl"]

        # At least 3 security topics should be mentioned
        security_mentions = sum(1 for topic in security_topics if topic in content)
        self.assertGreaterEqual(
            security_mentions,
            3,
            "Deployment guide should cover security considerations",
        )

    def test_deployment_guide_has_monitoring_section(self) -> None:
        """Test that deployment guide includes monitoring information."""
        self.assertTrue(self.deployment_guide_path.exists())
        content = self.deployment_guide_path.read_text().lower()

        monitoring_terms = ["logs", "monitoring", "health", "status"]

        monitoring_mentions = sum(1 for term in monitoring_terms if term in content)
        self.assertGreaterEqual(
            monitoring_mentions,
            2,
            "Deployment guide should include monitoring information",
        )

    def test_deployment_guide_references_docker_compose_file(self) -> None:
        """Test that deployment guide references the docker-compose.yml file."""
        self.assertTrue(self.deployment_guide_path.exists())
        content = self.deployment_guide_path.read_text()

        self.assertIn(
            "docker-compose.yml",
            content,
            "Deployment guide should reference docker-compose.yml",
        )

    def test_deployment_guide_has_proper_markdown_formatting(self) -> None:
        """Test that deployment guide uses proper markdown formatting."""
        self.assertTrue(self.deployment_guide_path.exists())
        content = self.deployment_guide_path.read_text()

        # Should have markdown headers
        self.assertIn("# ", content, "Should have level 1 headers")
        self.assertIn("## ", content, "Should have level 2 headers")

        # Should have code blocks
        self.assertIn("```", content, "Should have code blocks")

        # Should have bold/emphasis formatting
        markdown_formatting_count = content.count("**") + content.count("*")
        self.assertGreater(
            markdown_formatting_count, 0, "Should use markdown formatting for emphasis"
        )
