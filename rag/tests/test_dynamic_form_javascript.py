"""Tests for dynamic form JavaScript functionality."""

from pathlib import Path

from django.test import TestCase


class DynamicFormJavaScriptTest(TestCase):
    """Test that dynamic form switching JavaScript exists and is correct."""

    def test_context_type_selection_javascript_exists(self):
        """Test that JavaScript file for context type selection exists."""
        js_file_path = Path("rag/static/rag/js/context_type_selection.js")

        # The file should exist
        self.assertTrue(
            js_file_path.exists(),
            f"JavaScript file {js_file_path} should exist for dynamic form switching",
        )

    def test_context_type_selection_javascript_contains_required_functions(self):
        """Test that JavaScript contains required functions for dynamic forms."""
        js_file_path = Path("rag/static/rag/js/context_type_selection.js")

        if not js_file_path.exists():
            self.skipTest("JavaScript file does not exist yet")

        with open(js_file_path) as f:
            js_content = f.read()

        # Should contain function to handle context type changes
        self.assertIn(
            "contextTypeChanged",
            js_content,
            "JavaScript should contain contextTypeChanged function",
        )

        # Should contain logic to show/hide fields based on context type
        self.assertIn("PDF", js_content, "JavaScript should handle PDF context type")
        self.assertIn(
            "MARKDOWN", js_content, "JavaScript should handle MARKDOWN context type"
        )
        self.assertIn("FAQ", js_content, "JavaScript should handle FAQ context type")
