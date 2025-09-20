"""Tests for end user guide documentation."""

from __future__ import annotations

from pathlib import Path

from django.test import TestCase


class EndUserGuideTest(TestCase):
    """Test cases to validate end user guide documentation."""

    def setUp(self) -> None:
        """Set up test paths."""
        self.project_root = Path(__file__).parent.parent.parent
        self.user_guide_path = self.project_root / "docs" / "USER_GUIDE.md"

    def test_user_guide_exists(self) -> None:
        """Test that end user guide file exists."""
        self.assertTrue(
            self.user_guide_path.exists(),
            f"End user guide not found at {self.user_guide_path}",
        )

    def test_user_guide_has_content(self) -> None:
        """Test that end user guide has substantial content."""
        self.assertTrue(self.user_guide_path.exists())
        content = self.user_guide_path.read_text()

        # Should have substantial content (at least 1500 characters)
        self.assertGreater(
            len(content), 1500, "End user guide should have substantial content"
        )

    def test_user_guide_has_required_sections(self) -> None:
        """Test that end user guide contains all required sections."""
        self.assertTrue(self.user_guide_path.exists())
        content = self.user_guide_path.read_text().lower()

        required_sections = [
            "# user guide",
            "## getting started",
            "## topic selection",
            "## asking questions",
            "## understanding answers",
            "## sources and citations",
            "## tips for better results",
            "## troubleshooting",
            "## frequently asked questions",
        ]

        for section in required_sections:
            self.assertIn(
                section, content, f"End user guide missing required section: {section}"
            )

    def test_user_guide_contains_interface_elements(self) -> None:
        """Test that end user guide documents interface elements."""
        self.assertTrue(self.user_guide_path.exists())
        content = self.user_guide_path.read_text().lower()

        interface_elements = [
            "topic card",
            "question box",
            "ask question",
            "answer section",
            "citations",
            "sources",
        ]

        for element in interface_elements:
            self.assertIn(element, content, f"End user guide should document {element}")

    def test_user_guide_contains_user_actions(self) -> None:
        """Test that end user guide documents user actions."""
        self.assertTrue(self.user_guide_path.exists())
        content = self.user_guide_path.read_text().lower()

        user_actions = [
            "select a topic",
            "type your question",
            "click",
            "submit",
            "review the answer",
        ]

        for action in user_actions:
            self.assertIn(action, content, f"End user guide should document {action}")

    def test_user_guide_contains_question_guidelines(self) -> None:
        """Test that end user guide contains question writing guidelines."""
        self.assertTrue(self.user_guide_path.exists())
        content = self.user_guide_path.read_text().lower()

        question_guidelines = [
            "clear question",
            "specific",
            "context",
            "detailed",
            "effective questions",
        ]

        # At least 3 guidelines should be mentioned
        guideline_mentions = sum(
            1 for guideline in question_guidelines if guideline in content
        )
        self.assertGreaterEqual(
            guideline_mentions,
            3,
            "End user guide should include question writing guidelines",
        )

    def test_user_guide_contains_answer_interpretation(self) -> None:
        """Test that end user guide explains how to interpret answers."""
        self.assertTrue(self.user_guide_path.exists())
        content = self.user_guide_path.read_text().lower()

        answer_interpretation = [
            "answer format",
            "accuracy",
            "reliability",
            "citations",
            "source quality",
        ]

        interpretation_mentions = sum(
            1 for term in answer_interpretation if term in content
        )
        self.assertGreaterEqual(
            interpretation_mentions,
            3,
            "End user guide should explain answer interpretation",
        )

    def test_user_guide_has_troubleshooting_section(self) -> None:
        """Test that end user guide has troubleshooting information."""
        self.assertTrue(self.user_guide_path.exists())
        content = self.user_guide_path.read_text().lower()

        troubleshooting_terms = [
            "error",
            "problem",
            "troubleshooting",
            "common issues",
            "solution",
            "help",
        ]

        troubleshooting_mentions = sum(
            1 for term in troubleshooting_terms if term in content
        )
        self.assertGreaterEqual(
            troubleshooting_mentions,
            4,
            "End user guide should include troubleshooting information",
        )

    def test_user_guide_has_examples(self) -> None:
        """Test that end user guide includes practical examples."""
        self.assertTrue(self.user_guide_path.exists())
        content = self.user_guide_path.read_text().lower()

        example_terms = [
            "example",
            "sample",
            "for instance",
            "demonstration",
            "illustration",
        ]

        example_mentions = sum(1 for term in example_terms if term in content)
        self.assertGreaterEqual(
            example_mentions, 3, "End user guide should include practical examples"
        )

    def test_user_guide_has_proper_markdown_formatting(self) -> None:
        """Test that end user guide uses proper markdown formatting."""
        self.assertTrue(self.user_guide_path.exists())
        content = self.user_guide_path.read_text()

        # Should have markdown headers
        self.assertIn("# ", content, "Should have level 1 headers")
        self.assertIn("## ", content, "Should have level 2 headers")

        # Should have lists for steps and tips
        has_ordered_lists = any(
            line.strip().startswith(("1.", "2.", "3.")) for line in content.split("\n")
        )
        has_unordered_lists = any(
            line.strip().startswith(("- ", "* ")) for line in content.split("\n")
        )
        self.assertTrue(
            has_ordered_lists or has_unordered_lists,
            "Should have lists for procedures and tips",
        )

        # Should have emphasis formatting
        has_bold = "**" in content
        has_italic = "*" in content or "_" in content
        self.assertTrue(
            has_bold or has_italic, "Should use markdown formatting for emphasis"
        )

    def test_user_guide_contains_getting_started_steps(self) -> None:
        """Test that end user guide contains clear getting started steps."""
        self.assertTrue(self.user_guide_path.exists())
        content = self.user_guide_path.read_text().lower()

        getting_started_terms = ["step", "first", "navigate", "begin", "start"]

        steps_mentions = sum(1 for term in getting_started_terms if term in content)
        self.assertGreaterEqual(
            steps_mentions, 3, "End user guide should have clear getting started steps"
        )

    def test_user_guide_contains_faq_section(self) -> None:
        """Test that end user guide contains FAQ section."""
        self.assertTrue(self.user_guide_path.exists())
        content = self.user_guide_path.read_text().lower()

        faq_indicators = ["frequently asked", "common questions", "faq", "q:", "a:"]

        faq_mentions = sum(1 for indicator in faq_indicators if indicator in content)
        self.assertGreaterEqual(
            faq_mentions, 2, "End user guide should include FAQ section"
        )

    def test_user_guide_addresses_user_concerns(self) -> None:
        """Test that end user guide addresses common user concerns."""
        self.assertTrue(self.user_guide_path.exists())
        content = self.user_guide_path.read_text().lower()

        user_concerns = [
            "privacy",
            "accuracy",
            "reliability",
            "limitations",
            "feedback",
        ]

        concern_mentions = sum(1 for concern in user_concerns if concern in content)
        self.assertGreaterEqual(
            concern_mentions, 2, "End user guide should address user concerns"
        )
