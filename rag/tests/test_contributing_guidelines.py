"""Tests for contributing guidelines documentation."""

from __future__ import annotations

import re
from pathlib import Path

from django.test import TestCase


class ContributingGuidelinesTest(TestCase):
    """Test cases to validate contributing guidelines documentation."""

    def setUp(self) -> None:
        """Set up test paths."""
        self.project_root = Path(__file__).parent.parent.parent
        self.guidelines_path = self.project_root / "docs" / "CONTRIBUTING.md"

    def test_contributing_guidelines_exists(self) -> None:
        """Test that contributing guidelines file exists."""
        self.assertTrue(
            self.guidelines_path.exists(),
            f"Contributing guidelines not found at {self.guidelines_path}",
        )

    def test_contributing_guidelines_has_required_sections(self) -> None:
        """Test that contributing guidelines contain all required sections."""
        self.assertTrue(self.guidelines_path.exists())
        content = self.guidelines_path.read_text().lower()

        required_sections = [
            "# contributing to scholaria",
            "## project philosophy",
            "## before you start",
            "## workflow overview",
            "## branching strategy",
            "## coding standards",
            "## testing requirements",
            "## commit guidelines",
            "## pull request checklist",
            "## communication",
        ]

        for section in required_sections:
            self.assertRegex(
                content,
                rf"(?m)^\s*{re.escape(section)}\s*$",
                f"Contributing guidelines missing required section: {section}",
            )

    def test_contributing_guidelines_reference_quality_tools(self) -> None:
        """Test that contributing guidelines reference required quality tooling."""
        self.assertTrue(self.guidelines_path.exists())
        content = self.guidelines_path.read_text().lower()

        required_phrases = [
            "uv run ruff check .",
            "uv run mypy .",
            "python manage.py test",
            "docker-compose up",
            "pytest",
        ]

        for phrase in required_phrases:
            self.assertIn(
                phrase,
                content,
                f"Contributing guidelines should mention quality tool: {phrase}",
            )

    def test_contributing_guidelines_emphasize_tdd(self) -> None:
        """Test that contributing guidelines emphasize the TDD workflow."""
        self.assertTrue(self.guidelines_path.exists())
        content = self.guidelines_path.read_text().lower()

        tdd_keywords = ["tdd", "red → green → refactor", "tidy first"]
        for keyword in tdd_keywords:
            self.assertIn(
                keyword,
                content,
                f"Contributing guidelines should emphasize {keyword}",
            )

    def test_contributing_guidelines_include_support_channels(self) -> None:
        """Test that contributing guidelines document support channels."""
        self.assertTrue(self.guidelines_path.exists())
        content = self.guidelines_path.read_text().lower()

        support_terms = ["slack", "issue template", "docs/tasks.md", "agents"]
        for term in support_terms:
            self.assertIn(
                term,
                content,
                f"Contributing guidelines should mention support resource: {term}",
            )
