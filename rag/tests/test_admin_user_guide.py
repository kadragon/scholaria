"""Tests for admin user guide documentation."""

from __future__ import annotations

import re
from pathlib import Path

from django.test import TestCase


class AdminUserGuideTest(TestCase):
    """Test cases to validate admin user guide documentation."""

    def setUp(self) -> None:
        """Set up test paths."""
        self.project_root = Path(__file__).parent.parent.parent
        self.admin_guide_path = self.project_root / "docs" / "ADMIN_GUIDE.md"

    def test_admin_guide_exists(self) -> None:
        """Test that admin user guide file exists."""
        self.assertTrue(
            self.admin_guide_path.exists(),
            f"Admin user guide not found at {self.admin_guide_path}",
        )

    def test_admin_guide_has_content(self) -> None:
        """Test that admin user guide has substantial content."""
        self.assertTrue(self.admin_guide_path.exists())
        content = self.admin_guide_path.read_text()

        # Should have substantial content (at least 2000 characters)
        self.assertGreater(
            len(content), 2000, "Admin user guide should have substantial content"
        )

    def test_admin_guide_has_required_sections(self) -> None:
        """Test that admin user guide contains all required sections."""
        self.assertTrue(self.admin_guide_path.exists())
        content = self.admin_guide_path.read_text().lower()

        required_sections = [
            "# admin user guide",
            "## getting started",
            "## login",
            "## topic management",
            "## context management",
            "## context item management",
            "## file upload",
            "## bulk operations",
            "## best practices",
            "## troubleshooting",
        ]

        for section in required_sections:
            self.assertRegex(
                content,
                rf"(?m)^\s*{re.escape(section)}\s*$",
                f"Admin user guide missing required section: {section}",
            )

    def test_admin_guide_contains_topic_operations(self) -> None:
        """Test that admin user guide documents topic operations."""
        self.assertTrue(self.admin_guide_path.exists())
        content = self.admin_guide_path.read_text().lower()

        topic_operations = [
            "create topic",
            "edit topic",
            "system prompt",
            "assign context",
            "bulk update",
        ]

        for operation in topic_operations:
            self.assertIn(
                operation, content, f"Admin user guide should document {operation}"
            )

    def test_admin_guide_contains_context_operations(self) -> None:
        """Test that admin user guide documents context operations."""
        self.assertTrue(self.admin_guide_path.exists())
        content = self.admin_guide_path.read_text().lower()

        context_operations = [
            "create context",
            "context type",
            "pdf",
            "markdown",
            "faq",
        ]

        for operation in context_operations:
            self.assertIn(
                operation, content, f"Admin user guide should document {operation}"
            )

    def test_admin_guide_contains_file_upload_instructions(self) -> None:
        """Test that admin user guide contains file upload instructions."""
        self.assertTrue(self.admin_guide_path.exists())
        content = self.admin_guide_path.read_text().lower()

        file_upload_terms = [
            "upload",
            "file validation",
            "minio",
            "file size",
            "supported formats",
        ]

        for term in file_upload_terms:
            self.assertIn(term, content, f"Admin user guide should mention {term}")

    def test_admin_guide_contains_bulk_operations(self) -> None:
        """Test that admin user guide documents bulk operations."""
        self.assertTrue(self.admin_guide_path.exists())
        content = self.admin_guide_path.read_text().lower()

        bulk_operations = [
            "bulk operations",
            "select multiple",
            "assign context to topics",
            "update system prompt",
            "regenerate embeddings",
            "move to context",
        ]

        for operation in bulk_operations:
            self.assertIn(
                operation, content, f"Admin user guide should document {operation}"
            )

    def test_admin_guide_has_screenshots_references(self) -> None:
        """Test that admin user guide references screenshots or visual aids."""
        self.assertTrue(self.admin_guide_path.exists())
        content = self.admin_guide_path.read_text().lower()

        visual_references = ["screenshot", "image", "figure", "click", "button"]

        # At least 3 visual references should be mentioned
        visual_mentions = sum(1 for ref in visual_references if ref in content)
        self.assertGreaterEqual(
            visual_mentions, 3, "Admin user guide should include visual references"
        )

    def test_admin_guide_has_workflow_examples(self) -> None:
        """Test that admin user guide includes workflow examples."""
        self.assertTrue(self.admin_guide_path.exists())
        content = self.admin_guide_path.read_text().lower()

        workflow_terms = ["workflow", "step", "example", "process", "procedure"]

        workflow_mentions = sum(1 for term in workflow_terms if term in content)
        self.assertGreaterEqual(
            workflow_mentions, 3, "Admin user guide should include workflow examples"
        )

    def test_admin_guide_has_troubleshooting_section(self) -> None:
        """Test that admin user guide has troubleshooting information."""
        self.assertTrue(self.admin_guide_path.exists())
        content = self.admin_guide_path.read_text().lower()

        troubleshooting_terms = [
            "error",
            "problem",
            "troubleshooting",
            "common issues",
            "solution",
        ]

        troubleshooting_mentions = sum(
            1 for term in troubleshooting_terms if term in content
        )
        self.assertGreaterEqual(
            troubleshooting_mentions,
            3,
            "Admin user guide should include troubleshooting information",
        )

    def test_admin_guide_has_proper_markdown_formatting(self) -> None:
        """Test that admin user guide uses proper markdown formatting."""
        self.assertTrue(self.admin_guide_path.exists())
        content = self.admin_guide_path.read_text()

        # Should have markdown headers
        self.assertIn("# ", content, "Should have level 1 headers")
        self.assertIn("## ", content, "Should have level 2 headers")
        self.assertIn("### ", content, "Should have level 3 headers")

        # Should have code blocks or inline code
        has_code_blocks = "```" in content
        has_inline_code = "`" in content
        self.assertTrue(
            has_code_blocks or has_inline_code, "Should have code formatting"
        )

        # Should have lists
        has_ordered_lists = any(
            line.strip().startswith(("1.", "2.", "3.")) for line in content.split("\n")
        )
        has_unordered_lists = any(
            line.strip().startswith(("- ", "* ")) for line in content.split("\n")
        )
        self.assertTrue(
            has_ordered_lists or has_unordered_lists, "Should have lists for procedures"
        )

        # Should have bold/emphasis formatting
        markdown_formatting_count = content.count("**") + content.count("*")
        self.assertGreater(
            markdown_formatting_count, 0, "Should use markdown formatting for emphasis"
        )

    def test_admin_guide_contains_security_considerations(self) -> None:
        """Test that admin user guide includes security considerations."""
        self.assertTrue(self.admin_guide_path.exists())
        content = self.admin_guide_path.read_text().lower()

        security_terms = [
            "security",
            "password",
            "permission",
            "access",
            "authentication",
        ]

        security_mentions = sum(1 for term in security_terms if term in content)
        self.assertGreaterEqual(
            security_mentions,
            2,
            "Admin user guide should include security considerations",
        )
