from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from rag.models import Context


class FAQTwoPhaseWorkflowTest(TestCase):
    """Test the new two-phase FAQ creation workflow."""

    def test_faq_context_creation_phase_one(self):
        """
        Test Phase 1: Creating an empty FAQ context that can later have Q&A pairs added.
        """
        # Create an FAQ context
        context = Context.objects.create(
            name="Test FAQ Context",
            description="Test context for FAQ workflow",
            context_type="FAQ",
        )

        # Phase 1: Should create empty context ready for Q&A addition
        self.assertEqual(context.context_type, "FAQ")
        self.assertEqual(context.processing_status, "PENDING")
        self.assertEqual(context.chunk_count, 0)
        self.assertIsNone(context.original_content)  # No content yet

        # Should have no chunks initially
        chunks = context.items.all()
        self.assertFalse(chunks.exists())

    def test_faq_qa_pair_addition_phase_two(self):
        """
        Test Phase 2: Adding Q&A pairs to an FAQ context.
        Each Q&A pair should become a separate chunk.
        """
        # Create FAQ context (Phase 1)
        context = Context.objects.create(
            name="Test FAQ Context",
            description="Test context for FAQ workflow",
            context_type="FAQ",
        )

        # Phase 2: Add Q&A pairs using the new method
        success = context.add_qa_pair(
            question="What is the capital of France?",
            answer="The capital of France is Paris.",
        )

        # Verify the Q&A pair was added successfully
        self.assertTrue(success)

        # Refresh from database
        context.refresh_from_db()

        # Should have 1 chunk for the Q&A pair
        self.assertEqual(context.chunk_count, 1)

        # Check that the chunk was created correctly
        chunks = context.items.all()
        self.assertEqual(chunks.count(), 1)

        chunk = chunks.first()
        assert chunk is not None  # For mypy
        self.assertIn("What is the capital of France?", chunk.content)
        self.assertIn("The capital of France is Paris", chunk.content)
        self.assertEqual(chunk.title, "Test FAQ Context - Q&A 1")

    def test_faq_multiple_qa_pairs(self):
        """
        Test adding multiple Q&A pairs to an FAQ context.
        Each Q&A pair should become a separate chunk.
        """
        # Create FAQ context
        context = Context.objects.create(
            name="Multiple FAQ Context",
            description="Test context for multiple Q&A pairs",
            context_type="FAQ",
        )

        # Add first Q&A pair
        success1 = context.add_qa_pair(
            question="What is Python?", answer="Python is a programming language."
        )
        self.assertTrue(success1)

        # Add second Q&A pair
        success2 = context.add_qa_pair(
            question="What is Django?", answer="Django is a Python web framework."
        )
        self.assertTrue(success2)

        # Refresh from database
        context.refresh_from_db()

        # Should have 2 chunks for the 2 Q&A pairs
        self.assertEqual(context.chunk_count, 2)

        # Check that both chunks were created correctly
        chunks = context.items.all().order_by("created_at")
        self.assertEqual(chunks.count(), 2)

        # First chunk
        chunk1 = chunks[0]
        self.assertIn("What is Python?", chunk1.content)
        self.assertIn("Python is a programming language", chunk1.content)
        self.assertEqual(chunk1.title, "Multiple FAQ Context - Q&A 1")

        # Second chunk
        chunk2 = chunks[1]
        self.assertIn("What is Django?", chunk2.content)
        self.assertIn("Django is a Python web framework", chunk2.content)
        self.assertEqual(chunk2.title, "Multiple FAQ Context - Q&A 2")


class FAQAdminManagementTest(TestCase):
    """Test the Q&A pair management interface within Context admin."""

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username="admin", password="admin", is_staff=True, is_superuser=True
        )
        self.client.login(username="admin", password="admin")

    def test_faq_context_admin_form_loads_successfully(self):
        """Test that FAQ context admin form loads without errors."""
        # Create an FAQ context first
        context = Context.objects.create(
            name="Test FAQ Context",
            description="Test context for FAQ admin",
            context_type="FAQ",
        )

        # Access the admin change form for the FAQ context
        url = reverse("admin:rag_context_change", args=[context.pk])
        response = self.client.get(url)

        # Should load successfully
        self.assertEqual(response.status_code, 200)
        # Should contain the context name
        self.assertContains(response, "Test FAQ Context")

    def test_add_qa_pair_through_admin_action(self):
        """Test adding Q&A pairs through admin interface."""
        # Create an FAQ context
        Context.objects.create(
            name="Admin Test FAQ",
            description="Test context for admin Q&A addition",
            context_type="FAQ",
        )

        # Test the admin action for adding Q&A pairs
        url = reverse("admin:rag_context_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Check that the action exists
        self.assertContains(response, "add_qa_pair_action")

    def test_faq_inline_editor(self):
        """Test that FAQ contexts use the FAQ-specific inline editor."""
        # Create an FAQ context with Q&A pairs
        context = Context.objects.create(
            name="FAQ with Inline Context",
            description="Test context for FAQ inline editing",
            context_type="FAQ",
        )

        # Add a Q&A pair
        context.add_qa_pair(
            question="What is inline editing?",
            answer="Inline editing allows editing directly in the admin interface.",
        )

        # Access the admin change form
        url = reverse("admin:rag_context_change", args=[context.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # Should contain the Q&A content
        self.assertContains(response, "What is inline editing?")
        self.assertContains(response, "Inline editing allows editing")
