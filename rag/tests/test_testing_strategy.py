"""Tests for testing strategy documentation."""

from __future__ import annotations

import re
from pathlib import Path

from django.test import TestCase


class TestingStrategyTest(TestCase):
    """Test cases to validate testing strategy documentation."""

    def setUp(self) -> None:
        """Set up test paths."""
        self.project_root = Path(__file__).parent.parent.parent
        self.strategy_path = self.project_root / "docs" / "TESTING_STRATEGY.md"

    def test_testing_strategy_exists(self) -> None:
        """Test that testing strategy file exists."""
        self.assertTrue(
            self.strategy_path.exists(),
            f"Testing strategy not found at {self.strategy_path}",
        )

    def test_testing_strategy_has_required_sections(self) -> None:
        """Test that testing strategy contains all required sections."""
        self.assertTrue(self.strategy_path.exists())
        content = self.strategy_path.read_text().lower()

        required_sections = [
            "# testing strategy",
            "## project philosophy",
            "## testing framework & configuration",
            "## testing categories",
            "## tdd workflow",
            "## test commands",
            "## test organization principles",
            "## testing best practices",
            "## error handling & debugging",
            "## continuous integration",
            "## success metrics",
        ]

        for section in required_sections:
            self.assertRegex(
                content,
                rf"(?m)^\s*{re.escape(section)}\s*$",
                f"Testing strategy missing required section: {section}",
            )

    def test_testing_strategy_documents_tdd_workflow(self) -> None:
        """Test that testing strategy documents TDD workflow phases."""
        self.assertTrue(self.strategy_path.exists())
        content = self.strategy_path.read_text().lower()

        tdd_phases = ["red phase", "green phase", "refactor phase"]
        for phase in tdd_phases:
            self.assertIn(
                phase,
                content,
                f"Testing strategy should document TDD {phase}",
            )

        # Verify TDD cycle terminology
        tdd_keywords = ["red → green → refactor", "tidy first"]
        for keyword in tdd_keywords:
            self.assertIn(
                keyword,
                content,
                f"Testing strategy should reference {keyword}",
            )

    def test_testing_strategy_references_test_tools(self) -> None:
        """Test that testing strategy references all testing tools."""
        self.assertTrue(self.strategy_path.exists())
        content = self.strategy_path.read_text().lower()

        required_tools = [
            "django testcase",
            "pytest",
            "factory boy",
            "pytest-celery",
            "pytest-xdist",
            "ruff",
            "mypy",
        ]

        for tool in required_tools:
            self.assertIn(
                tool,
                content,
                f"Testing strategy should reference testing tool: {tool}",
            )

    def test_testing_strategy_documents_test_categories(self) -> None:
        """Test that testing strategy documents all test categories."""
        self.assertTrue(self.strategy_path.exists())
        content = self.strategy_path.read_text().lower()

        test_categories = [
            "unit tests",
            "integration tests",
            "end-to-end tests",
            "documentation tests",
            "performance tests",
            "infrastructure tests",
        ]

        for category in test_categories:
            self.assertIn(
                category,
                content,
                f"Testing strategy should document {category}",
            )

    def test_testing_strategy_includes_test_commands(self) -> None:
        """Test that testing strategy includes essential test commands."""
        self.assertTrue(self.strategy_path.exists())
        content = self.strategy_path.read_text().lower()

        required_commands = [
            "uv run python manage.py test",
            "uv run pytest",
            "uv run ruff check",
            "uv run mypy",
            "--settings=core.test_settings",
        ]

        for command in required_commands:
            self.assertIn(
                command,
                content,
                f"Testing strategy should include command: {command}",
            )

    def test_testing_strategy_documents_current_status(self) -> None:
        """Test that testing strategy documents current test metrics."""
        self.assertTrue(self.strategy_path.exists())
        content = self.strategy_path.read_text().lower()

        status_indicators = [
            "134/134 tests passing",
            "success metrics",
            "target metrics",
        ]

        for indicator in status_indicators:
            self.assertIn(
                indicator,
                content,
                f"Testing strategy should include status: {indicator}",
            )

    def test_testing_strategy_references_test_files(self) -> None:
        """Test that testing strategy references actual test file examples."""
        self.assertTrue(self.strategy_path.exists())
        content = self.strategy_path.read_text().lower()

        test_file_examples = [
            "test_models.py",
            "test_ingestion.py",
            "test_contributing_guidelines.py",
            "test_e2e_integration.py",
        ]

        for test_file in test_file_examples:
            self.assertIn(
                test_file,
                content,
                f"Testing strategy should reference test file: {test_file}",
            )
