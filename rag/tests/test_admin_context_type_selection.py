"""Tests for context type selection workflow in admin interface."""

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from rag.admin import ContextAdmin, ContextForm
from rag.models import Context


class ContextTypeSelectionWorkflowTest(TestCase):
    """Test dynamic form switching based on context_type selection."""

    def setUp(self):
        self.admin_site = AdminSite()
        self.context_admin = ContextAdmin(Context, self.admin_site)
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser("admin", "admin@test.com", "password")

    def test_context_form_initializes_with_dynamic_behavior(self):
        """Test that ContextForm includes context type selection logic."""
        form = ContextForm()

        # Form should have context_type field
        self.assertIn("context_type", form.fields)

        # Form should have uploaded_file field for PDF contexts
        self.assertIn("uploaded_file", form.fields)

    def test_context_form_shows_appropriate_fields_for_pdf_type(self):
        """Test that PDF context type shows file upload field."""
        # Simulate form data for PDF context
        form_data = {
            "name": "Test PDF Context",
            "description": "Test description",
            "context_type": "PDF",
            "processing_status": "PENDING",
            "chunk_count": 0,
        }

        form = ContextForm(data=form_data)

        # The form should be valid for PDF type
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

        # uploaded_file field should be available for PDF
        self.assertIn("uploaded_file", form.fields)

    def test_context_form_validation_for_markdown_type(self):
        """Test that Markdown context type works correctly."""
        form_data = {
            "name": "Test Markdown Context",
            "description": "Test description",
            "context_type": "MARKDOWN",
            "processing_status": "PENDING",
            "chunk_count": 0,
            "original_content": "# Test Markdown\n\nThis is test content.",
        }

        form = ContextForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_context_form_validation_for_faq_type(self):
        """Test that FAQ context type works correctly."""
        form_data = {
            "name": "Test FAQ Context",
            "description": "Test description",
            "context_type": "FAQ",
            "processing_status": "PENDING",
            "chunk_count": 0,
        }

        form = ContextForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_admin_fieldsets_change_based_on_context_type(self):
        """Test that admin fieldsets are dynamic based on context type."""
        request = self.factory.get("/")
        request.user = self.user

        # Test PDF context fieldsets
        pdf_context = Context(
            name="PDF Test", description="PDF description", context_type="PDF"
        )
        pdf_fieldsets = self.context_admin.get_fieldsets(request, pdf_context)

        # Should have file upload fieldset for PDF
        fieldset_names = [fieldset[0] for fieldset in pdf_fieldsets]
        self.assertIn("File Upload", fieldset_names)

        # Test Markdown context fieldsets
        markdown_context = Context(
            name="Markdown Test",
            description="Markdown description",
            context_type="MARKDOWN",
        )
        markdown_fieldsets = self.context_admin.get_fieldsets(request, markdown_context)

        # Should have markdown content fieldset
        fieldset_names = [fieldset[0] for fieldset in markdown_fieldsets]
        self.assertIn("Markdown Content", fieldset_names)

    def test_dynamic_inlines_based_on_context_type(self):
        """Test that inline admins change based on context type."""
        request = self.factory.get("/")
        request.user = self.user

        # Test FAQ context inlines
        faq_context = Context(
            name="FAQ Test", description="FAQ description", context_type="FAQ"
        )
        faq_context.save()

        faq_inlines = self.context_admin.get_inline_instances(request, faq_context)
        # Should have FAQ-specific inline
        self.assertTrue(len(faq_inlines) > 0)

        # Test Markdown context inlines
        markdown_context = Context(
            name="Markdown Test",
            description="Markdown description",
            context_type="MARKDOWN",
        )
        markdown_context.save()

        markdown_inlines = self.context_admin.get_inline_instances(
            request, markdown_context
        )
        # Should have Markdown-specific inline
        self.assertTrue(len(markdown_inlines) > 0)
