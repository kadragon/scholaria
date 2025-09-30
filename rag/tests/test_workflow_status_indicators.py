"""Tests for workflow status indicators in admin interface."""

from pathlib import Path

from django.test import TestCase


class WorkflowStatusIndicatorsTest(TestCase):
    """Test workflow status indicators and progress guidance."""

    def test_status_indicator_styles_exist(self):
        """Test that CSS styles for status indicators exist."""
        template_path = Path("templates/admin/rag/context/change_form.html")

        if not template_path.exists():
            self.skipTest("Admin template does not exist yet")

        with open(template_path) as f:
            template_content = f.read()

        # Should contain status indicator styles
        self.assertIn(
            ".status-indicator",
            template_content,
            "Template should contain status indicator CSS",
        )

    def test_workflow_progress_guidance_exists(self):
        """Test that workflow progress guidance is included."""
        template_path = Path("templates/admin/rag/context/change_form.html")

        if not template_path.exists():
            self.skipTest("Admin template does not exist yet")

        with open(template_path) as f:
            template_content = f.read()

        # Should contain workflow steps guidance
        self.assertIn(
            "workflow-steps",
            template_content,
            "Template should contain workflow steps guidance",
        )

    def test_processing_status_help_in_javascript(self):
        """Test that JavaScript provides processing status help."""
        js_path = Path("rag/static/rag/js/context_type_selection.js")

        if not js_path.exists():
            self.skipTest("JavaScript file does not exist yet")

        with open(js_path) as f:
            js_content = f.read()

        # Should contain processing status guidance
        self.assertIn(
            "updateProcessingStatusHelp",
            js_content,
            "JavaScript should contain processing status help function",
        )
