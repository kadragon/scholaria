"""Tests for contextual help and workflow guidance in admin interface."""

from pathlib import Path

from django.test import TestCase


class ContextualHelpWorkflowTest(TestCase):
    """Test contextual help and workflow guidance features."""

    def test_admin_change_form_template_exists(self):
        """Test that custom admin change form template exists."""
        template_path = Path("templates/admin/rag/context/change_form.html")

        self.assertTrue(
            template_path.exists(),
            f"Custom admin template {template_path} should exist",
        )

    def test_admin_template_contains_context_type_guide(self):
        """Test that admin template contains context type guidance."""
        template_path = Path("templates/admin/rag/context/change_form.html")

        if not template_path.exists():
            self.skipTest("Admin template does not exist yet")

        with open(template_path) as f:
            template_content = f.read()

        # Should contain help section
        self.assertIn(
            "context-type-help",
            template_content,
            "Template should contain context type help section",
        )

        # Should contain guidance for each context type
        self.assertIn("PDF:", template_content, "Template should contain PDF guidance")
        self.assertIn(
            "Markdown:", template_content, "Template should contain Markdown guidance"
        )
        self.assertIn("FAQ:", template_content, "Template should contain FAQ guidance")

        # Should include JavaScript for dynamic behavior
        self.assertIn(
            "context_type_selection.js",
            template_content,
            "Template should include dynamic form JavaScript",
        )

    def test_admin_template_contains_styling_for_help_sections(self):
        """Test that admin template includes styling for help sections."""
        template_path = Path("templates/admin/rag/context/change_form.html")

        if not template_path.exists():
            self.skipTest("Admin template does not exist yet")

        with open(template_path) as f:
            template_content = f.read()

        # Should contain CSS styling for help elements
        self.assertIn(
            ".context-type-help",
            template_content,
            "Template should contain CSS for help sections",
        )
        self.assertIn(
            ".fieldset-description",
            template_content,
            "Template should contain CSS for fieldset descriptions",
        )

    def test_workflow_guidance_in_javascript(self):
        """Test that JavaScript provides workflow guidance."""
        js_path = Path("rag/static/rag/js/context_type_selection.js")

        if not js_path.exists():
            self.skipTest("JavaScript file does not exist yet")

        with open(js_path) as f:
            js_content = f.read()

        # Should contain workflow guidance functions
        self.assertIn(
            "updateFieldsetDescription",
            js_content,
            "JavaScript should contain function to update descriptions",
        )
        self.assertIn(
            "updateUploadedFileHelp",
            js_content,
            "JavaScript should contain function to update file help",
        )

        # Should contain specific workflow messages
        self.assertIn(
            "automatically parse and create chunks",
            js_content,
            "JavaScript should contain PDF workflow guidance",
        )
        self.assertIn(
            "Edit markdown content directly",
            js_content,
            "JavaScript should contain Markdown workflow guidance",
        )
        self.assertIn(
            "Add Q&A Pair",
            js_content,
            "JavaScript should contain FAQ workflow guidance",
        )
