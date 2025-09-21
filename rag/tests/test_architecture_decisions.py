"""Tests for architecture decision records documentation."""

from __future__ import annotations

import re
from pathlib import Path

from django.test import TestCase


class ArchitectureDecisionsTest(TestCase):
    """Test cases to validate architecture decision records documentation."""

    def setUp(self) -> None:
        """Set up test paths."""
        self.project_root = Path(__file__).parent.parent.parent
        self.adr_path = self.project_root / "docs" / "ARCHITECTURE_DECISIONS.md"

    def test_architecture_decisions_exists(self) -> None:
        """Test that architecture decisions file exists."""
        self.assertTrue(
            self.adr_path.exists(),
            f"Architecture decisions not found at {self.adr_path}",
        )

    def test_architecture_decisions_has_required_sections(self) -> None:
        """Test that architecture decisions contains all required sections."""
        self.assertTrue(self.adr_path.exists())
        content = self.adr_path.read_text().lower()

        required_sections = [
            "# architecture decision records (adrs)",
            "## overview",
            "## decision process",
            "## future considerations",
        ]

        for section in required_sections:
            self.assertRegex(
                content,
                rf"(?m)^\s*{re.escape(section)}\s*$",
                f"Architecture decisions missing required section: {section}",
            )

    def test_architecture_decisions_documents_key_adrs(self) -> None:
        """Test that architecture decisions documents key architectural decisions."""
        self.assertTrue(self.adr_path.exists())
        content = self.adr_path.read_text().lower()

        key_decisions = [
            "adr-001: django as web framework",
            "adr-002: context-topic many-to-many relationship",
            "adr-003: context-centric data model",
            "adr-004: docling for pdf processing",
            "adr-005: celery for asynchronous processing",
            "adr-006: qdrant for vector storage",
            "adr-007: openai for embeddings and generation",
            "adr-008: test-driven development methodology",
            "adr-009: docker compose for development environment",
            "adr-010: structured logging and monitoring",
        ]

        for decision in key_decisions:
            self.assertIn(
                decision,
                content,
                f"Architecture decisions should document: {decision}",
            )

    def test_architecture_decisions_follows_adr_format(self) -> None:
        """Test that ADRs follow standard format with required fields."""
        self.assertTrue(self.adr_path.exists())
        content = self.adr_path.read_text().lower()

        adr_format_elements = [
            "**status**:",
            "**date**:",
            "**context**:",
            "### decision",
            "### rationale",
            "### consequences",
        ]

        for element in adr_format_elements:
            self.assertIn(
                element,
                content,
                f"ADRs should follow standard format including: {element}",
            )

    def test_architecture_decisions_references_technologies(self) -> None:
        """Test that architecture decisions reference key technologies."""
        self.assertTrue(self.adr_path.exists())
        content = self.adr_path.read_text().lower()

        technologies = [
            "django",
            "docling",
            "celery",
            "redis",
            "qdrant",
            "openai",
            "docker",
            "postgres",
        ]

        for tech in technologies:
            self.assertIn(
                tech,
                content,
                f"Architecture decisions should reference technology: {tech}",
            )

    def test_architecture_decisions_emphasize_tdd(self) -> None:
        """Test that architecture decisions emphasize TDD methodology."""
        self.assertTrue(self.adr_path.exists())
        content = self.adr_path.read_text().lower()

        tdd_concepts = [
            "test-driven development",
            "red → green → refactor",
            "tidy first",
            "regression testing",
        ]

        for concept in tdd_concepts:
            self.assertIn(
                concept,
                content,
                f"Architecture decisions should emphasize TDD concept: {concept}",
            )

    def test_architecture_decisions_includes_evaluation_criteria(self) -> None:
        """Test that architecture decisions include evaluation criteria."""
        self.assertTrue(self.adr_path.exists())
        content = self.adr_path.read_text().lower()

        criteria = [
            "evaluation criteria",
            "scalability",
            "maintainability",
            "performance",
            "cost",
            "risk",
        ]

        for criterion in criteria:
            self.assertIn(
                criterion,
                content,
                f"Architecture decisions should include criterion: {criterion}",
            )

    def test_architecture_decisions_documents_consequences(self) -> None:
        """Test that architecture decisions document positive and negative consequences."""
        self.assertTrue(self.adr_path.exists())
        content = self.adr_path.read_text().lower()

        consequence_indicators = [
            "**positive:**",
            "**negative:**",
            "consequences",
        ]

        for indicator in consequence_indicators:
            self.assertIn(
                indicator,
                content,
                f"Architecture decisions should document: {indicator}",
            )

    def test_architecture_decisions_includes_code_examples(self) -> None:
        """Test that architecture decisions include relevant code examples."""
        self.assertTrue(self.adr_path.exists())
        content = self.adr_path.read_text()

        # Check for code blocks (markdown format)
        code_blocks = re.findall(r"```\w*\n.*?\n```", content, re.DOTALL)
        self.assertGreaterEqual(
            len(code_blocks),
            5,
            "Architecture decisions should include code examples",
        )

        # Check for specific code examples
        code_examples = [
            "class Topic(models.Model):",
            "class Context(models.Model):",
            "@shared_task",
            "DocumentConverter",
        ]

        for example in code_examples:
            self.assertIn(
                example,
                content,
                f"Architecture decisions should include code example: {example}",
            )
