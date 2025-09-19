from typing import cast

from django.contrib import admin
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile, UploadedFile
from django.test import Client, TestCase
from django.utils.datastructures import MultiValueDict

from rag.admin import ContextItemForm
from rag.models import Context, ContextItem, Topic


class AdminTestBase(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="admin", email="admin@test.com", password="testpass"
        )
        self.client = Client()
        self.client.login(username="admin", password="testpass")


class TopicAdminTest(AdminTestBase):
    def test_topic_admin_is_registered(self):
        """Test that Topic model is registered in admin."""
        self.assertIn(Topic, admin.site._registry)

    def test_topic_admin_list_display(self):
        """Test Topic admin list display configuration."""
        topic_admin = admin.site._registry[Topic]
        expected_fields = ["name", "description", "created_at", "updated_at"]
        self.assertEqual(list(topic_admin.list_display), expected_fields)

    def test_topic_admin_list_filter(self):
        """Test Topic admin list filter configuration."""
        topic_admin = admin.site._registry[Topic]
        expected_filters = ["created_at", "updated_at"]
        self.assertEqual(list(topic_admin.list_filter), expected_filters)

    def test_topic_admin_search_fields(self):
        """Test Topic admin search fields configuration."""
        topic_admin = admin.site._registry[Topic]
        expected_fields = ["name", "description"]
        self.assertEqual(list(topic_admin.search_fields), expected_fields)

    def test_topic_admin_fieldsets(self):
        """Test Topic admin fieldsets configuration."""
        topic_admin = admin.site._registry[Topic]
        expected_fieldsets = (
            (None, {"fields": ("name", "description", "system_prompt")}),
            ("Relationships", {"fields": ("contexts",)}),
        )
        self.assertEqual(topic_admin.fieldsets, expected_fieldsets)

    def test_topic_admin_contexts_field_included(self):
        """Test that contexts field is included in Topic admin fieldsets."""
        topic_admin = admin.site._registry[Topic]
        all_fields: list[str] = []
        fieldsets = topic_admin.fieldsets
        if fieldsets:
            for fieldset in fieldsets:
                fields = fieldset[1]["fields"]
                if isinstance(fields, list | tuple):
                    for field in fields:
                        if isinstance(field, str):
                            all_fields.append(field)
        self.assertIn("contexts", all_fields)

    def test_topic_admin_contexts_in_relationships_fieldset(self):
        """Test that contexts field is in the Relationships fieldset."""
        topic_admin = admin.site._registry[Topic]
        # Find the Relationships fieldset
        relationships_fieldset = None
        fieldsets = topic_admin.fieldsets
        if fieldsets:
            for fieldset in fieldsets:
                if fieldset[0] == "Relationships":
                    relationships_fieldset = fieldset
                    break

        self.assertIsNotNone(relationships_fieldset)
        if relationships_fieldset:
            self.assertIn("contexts", relationships_fieldset[1]["fields"])


class ContextAdminTest(AdminTestBase):
    def test_context_admin_is_registered(self):
        """Test that Context model is registered in admin."""
        self.assertIn(Context, admin.site._registry)

    def test_context_admin_list_display(self):
        """Test Context admin list display configuration."""
        context_admin = admin.site._registry[Context]
        expected_fields = ["name", "context_type", "description", "created_at"]
        self.assertEqual(list(context_admin.list_display), expected_fields)

    def test_context_admin_list_filter(self):
        """Test Context admin list filter configuration."""
        context_admin = admin.site._registry[Context]
        expected_filters = ["context_type", "created_at", "updated_at"]
        self.assertEqual(list(context_admin.list_filter), expected_filters)

    def test_context_admin_search_fields(self):
        """Test Context admin search fields configuration."""
        context_admin = admin.site._registry[Context]
        expected_fields = ["name", "description"]
        self.assertEqual(list(context_admin.search_fields), expected_fields)


class ContextItemAdminTest(AdminTestBase):
    def test_contextitem_admin_is_registered(self):
        """Test that ContextItem model is registered in admin."""
        self.assertIn(ContextItem, admin.site._registry)

    def test_contextitem_admin_list_display(self):
        """Test ContextItem admin list display configuration."""
        contextitem_admin = admin.site._registry[ContextItem]
        expected_fields = [
            "title",
            "context",
            "file_path",
            "has_uploaded_file",
            "created_at",
        ]
        self.assertEqual(list(contextitem_admin.list_display), expected_fields)

    def test_contextitem_admin_list_filter(self):
        """Test ContextItem admin list filter configuration."""
        contextitem_admin = admin.site._registry[ContextItem]
        expected_filters = ["context", "created_at", "updated_at"]
        self.assertEqual(list(contextitem_admin.list_filter), expected_filters)

    def test_contextitem_admin_search_fields(self):
        """Test ContextItem admin search fields configuration."""
        contextitem_admin = admin.site._registry[ContextItem]
        expected_fields = ["title", "content"]
        self.assertEqual(list(contextitem_admin.search_fields), expected_fields)

    def test_contextitem_admin_readonly_fields(self):
        """Test ContextItem admin readonly fields configuration."""
        contextitem_admin = admin.site._registry[ContextItem]
        expected_fields = ["created_at", "updated_at", "file_path"]
        self.assertEqual(list(contextitem_admin.readonly_fields), expected_fields)


class TopicContextMappingAdminTest(AdminTestBase):
    def setUp(self):
        super().setUp()
        self.topic = Topic.objects.create(
            name="Mathematics", description="Mathematical concepts and problem solving"
        )
        self.context1 = Context.objects.create(
            name="Math Textbook",
            description="Comprehensive mathematics textbook",
            context_type="PDF",
        )
        self.context2 = Context.objects.create(
            name="Math FAQ",
            description="Frequently asked questions about mathematics",
            context_type="FAQ",
        )

    def test_topic_admin_can_manage_context_relationships(self):
        """Test that Topic admin can add and remove context relationships."""
        # Verify we can access the topic change page
        url = f"/admin/rag/topic/{self.topic.id}/change/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Verify contexts field is in the form
        self.assertContains(response, 'name="contexts"')

    def test_topic_admin_save_with_contexts(self):
        """Test saving a topic with context relationships through admin."""
        url = f"/admin/rag/topic/{self.topic.id}/change/"
        data = {
            "name": self.topic.name,
            "description": self.topic.description,
            "system_prompt": "",
            "contexts": [self.context1.id, self.context2.id],
        }
        response = self.client.post(url, data)

        # Should redirect on successful save
        self.assertEqual(response.status_code, 302)

        # Verify the relationships were saved
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.contexts.count(), 2)
        self.assertIn(self.context1, self.topic.contexts.all())
        self.assertIn(self.context2, self.topic.contexts.all())

    def test_topic_admin_context_selection_widget(self):
        """Test that context selection widget shows available contexts."""
        url = f"/admin/rag/topic/{self.topic.id}/change/"
        response = self.client.get(url)

        # Should show both contexts as options
        self.assertContains(response, self.context1.name)
        self.assertContains(response, self.context2.name)


class ContextItemFormTest(TestCase):
    def setUp(self):
        self.context = Context.objects.create(
            name="Test Context",
            description="Test context for form validation",
            context_type="PDF",
        )

    def test_valid_pdf_file_upload(self):
        """Test that valid PDF files are accepted."""
        pdf_content = b"%PDF-1.4\nTest PDF content"
        uploaded_file = SimpleUploadedFile(
            name="test.pdf", content=pdf_content, content_type="application/pdf"
        )

        form_data = {
            "title": "Test Document",
            "content": "Test content",
            "context": self.context.id,
        }

        files = MultiValueDict({"uploaded_file": [cast(UploadedFile, uploaded_file)]})
        form = ContextItemForm(data=form_data, files=files)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_invalid_file_type_rejected(self):
        """Test that invalid file types are rejected."""
        exe_content = b"MZ\x90\x00"  # PE header for executable
        uploaded_file = SimpleUploadedFile(
            name="malware.exe",
            content=exe_content,
            content_type="application/octet-stream",
        )

        form_data = {
            "title": "Test Document",
            "content": "Test content",
            "context": self.context.id,
        }

        files = MultiValueDict({"uploaded_file": [cast(UploadedFile, uploaded_file)]})
        form = ContextItemForm(data=form_data, files=files)
        self.assertFalse(form.is_valid())
        self.assertIn("uploaded_file", form.errors)
        self.assertIn("File validation failed", str(form.errors["uploaded_file"]))

    def test_large_file_rejected(self):
        """Test that large files are rejected."""
        # Create a file larger than max size (10MB)
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        uploaded_file = SimpleUploadedFile(
            name="large.pdf", content=large_content, content_type="application/pdf"
        )

        form_data = {
            "title": "Test Document",
            "content": "Test content",
            "context": self.context.id,
        }

        files = MultiValueDict({"uploaded_file": [cast(UploadedFile, uploaded_file)]})
        form = ContextItemForm(data=form_data, files=files)
        self.assertFalse(form.is_valid())
        self.assertIn("uploaded_file", form.errors)
        self.assertIn("File size exceeds maximum", str(form.errors["uploaded_file"]))

    def test_filename_sanitization(self):
        """Test that filenames are sanitized."""
        pdf_content = b"%PDF-1.4\nTest PDF content"
        uploaded_file = SimpleUploadedFile(
            name="My Document!@#$.pdf",
            content=pdf_content,
            content_type="application/pdf",
        )

        form_data = {
            "title": "Test Document",
            "content": "Test content",
            "context": self.context.id,
        }

        files = MultiValueDict({"uploaded_file": [cast(UploadedFile, uploaded_file)]})
        form = ContextItemForm(data=form_data, files=files)
        self.assertTrue(form.is_valid())

        # Check that filename was sanitized
        cleaned_file = form.cleaned_data["uploaded_file"]
        self.assertEqual(cleaned_file.name, "my_document_.pdf")

    def test_form_without_file_valid(self):
        """Test that form is valid without uploaded file if content is provided."""
        form_data = {
            "title": "Test Document",
            "content": "Test content without file",
            "context": self.context.id,
        }

        form = ContextItemForm(data=form_data)
        self.assertTrue(form.is_valid())


class BulkOperationsAdminTest(AdminTestBase):
    """Test bulk operations in admin interface."""

    def setUp(self):
        super().setUp()

        # Create test topics
        self.topics = [
            Topic.objects.create(
                name=f"Topic {i}",
                description=f"Description for topic {i}",
                system_prompt=f"System prompt {i}",
            )
            for i in range(1, 6)
        ]

        # Create test contexts
        self.contexts = [
            Context.objects.create(
                name=f"Context {i}",
                description=f"Description for context {i}",
                context_type="PDF" if i % 2 == 0 else "FAQ",
            )
            for i in range(1, 6)
        ]

        # Create test context items
        self.context_items = [
            ContextItem.objects.create(
                title=f"Item {i}",
                content=f"Content for item {i}",
                context=self.contexts[i % len(self.contexts)],
            )
            for i in range(1, 11)
        ]

    def test_topic_bulk_delete_admin_action(self):
        """Test bulk delete action for topics in admin."""
        url = "/admin/rag/topic/"

        # Select multiple topics for deletion
        data = {
            "action": "delete_selected",
            "_selected_action": [self.topics[0].id, self.topics[1].id],
            "post": "yes",  # Confirm deletion
        }

        # Perform bulk delete
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Verify topics were deleted
        remaining_topics = Topic.objects.filter(
            id__in=[self.topics[0].id, self.topics[1].id]
        )
        self.assertEqual(remaining_topics.count(), 0)

        # Verify other topics remain
        self.assertEqual(Topic.objects.count(), 3)

    def test_context_bulk_delete_admin_action(self):
        """Test bulk delete action for contexts in admin."""
        url = "/admin/rag/context/"

        # Select multiple contexts for deletion
        data = {
            "action": "delete_selected",
            "_selected_action": [self.contexts[0].id, self.contexts[1].id],
            "post": "yes",  # Confirm deletion
        }

        # Perform bulk delete
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Verify contexts were deleted
        remaining_contexts = Context.objects.filter(
            id__in=[self.contexts[0].id, self.contexts[1].id]
        )
        self.assertEqual(remaining_contexts.count(), 0)

        # Verify other contexts remain
        self.assertEqual(Context.objects.count(), 3)

    def test_contextitem_bulk_delete_admin_action(self):
        """Test bulk delete action for context items in admin."""
        url = "/admin/rag/contextitem/"

        # Select multiple context items for deletion
        selected_items = [self.context_items[0].id, self.context_items[1].id]
        data = {
            "action": "delete_selected",
            "_selected_action": selected_items,
            "post": "yes",  # Confirm deletion
        }

        # Perform bulk delete
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Verify context items were deleted
        remaining_items = ContextItem.objects.filter(id__in=selected_items)
        self.assertEqual(remaining_items.count(), 0)

        # Verify other items remain
        self.assertEqual(ContextItem.objects.count(), 8)

    def test_bulk_delete_confirmation_page(self):
        """Test that bulk delete shows confirmation page."""
        url = "/admin/rag/topic/"

        # Select multiple topics but don't confirm
        data = {
            "action": "delete_selected",
            "_selected_action": [self.topics[0].id, self.topics[1].id],
            # No "post": "yes" to confirm
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

        # Should show confirmation page
        self.assertContains(response, "Are you sure you want to delete")
        self.assertContains(response, self.topics[0].name)
        self.assertContains(response, self.topics[1].name)

        # Topics should still exist
        self.assertEqual(Topic.objects.count(), 5)

    def test_bulk_topic_context_mapping(self):
        """Test bulk assignment of contexts to topics."""
        # This would be a custom admin action we'd implement
        url = "/admin/rag/topic/"

        # First test the change list page loads
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Verify topics are displayed
        for topic in self.topics:
            self.assertContains(response, topic.name)

    def test_bulk_filter_and_search(self):
        """Test bulk operations work with filters and search."""
        # Test Context admin with type filter
        url = "/admin/rag/context/?context_type=PDF"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Should show only PDF contexts
        pdf_contexts = [c for c in self.contexts if c.context_type == "PDF"]
        for context in pdf_contexts:
            self.assertContains(response, context.name)

        # Test search functionality
        url = "/admin/rag/topic/?q=Topic 1"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Topic 1")

    def test_bulk_operations_preserve_pagination(self):
        """Test that bulk operations work correctly with pagination."""
        # Create more topics to trigger pagination
        for i in range(1, 21):  # Create 20 more topics
            Topic.objects.create(
                name=f"Additional Topic {i}", description=f"Description {i}"
            )

        url = "/admin/rag/topic/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Should handle pagination
        total_topics = Topic.objects.count()
        self.assertGreaterEqual(total_topics, 25)

    def test_bulk_context_type_filter(self):
        """Test filtering contexts by type for bulk operations."""
        # Filter by PDF context type
        url = "/admin/rag/context/?context_type=PDF"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Count PDF contexts in our test data
        pdf_count = len([c for c in self.contexts if c.context_type == "PDF"])
        self.assertGreater(pdf_count, 0)

        # Filter by FAQ context type
        url = "/admin/rag/context/?context_type=FAQ"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_bulk_operations_error_handling(self):
        """Test error handling in bulk operations."""
        url = "/admin/rag/topic/"

        # Try bulk delete with invalid IDs
        data = {
            "action": "delete_selected",
            "_selected_action": [99999, 99998],  # Non-existent IDs
            "post": "yes",
        }

        response = self.client.post(url, data, follow=True)
        # Should handle gracefully (Django admin handles this)
        self.assertEqual(response.status_code, 200)

    def test_bulk_assign_context_to_topics_action(self):
        """Test custom bulk action to assign contexts to multiple topics."""
        url = "/admin/rag/topic/"

        # Test the action is available first
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Verify topics are displayed
        for topic in self.topics:
            self.assertContains(response, topic.name)

        # Test the bulk action form submission
        selected_topics = [self.topics[0].id, self.topics[1].id]
        context_to_assign = self.contexts[0]

        # First, trigger the action to get the form
        data = {
            "action": "assign_context_to_topics",
            "_selected_action": [str(tid) for tid in selected_topics],
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Assign Context to Topics")

        # Now submit the actual assignment
        data = {
            "action": "assign_context_to_topics",
            "_selected_action": [str(tid) for tid in selected_topics],
            "context_id": str(context_to_assign.id),
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Verify the context was assigned to the topics
        for topic_id in selected_topics:
            topic = Topic.objects.get(id=topic_id)
            self.assertIn(context_to_assign, topic.contexts.all())

    def test_bulk_update_system_prompt_action(self):
        """Test custom bulk action to update system prompt for topics."""
        url = "/admin/rag/topic/"

        # Test the bulk action form submission
        selected_topics = [self.topics[0].id, self.topics[1].id]
        new_system_prompt = "Updated system prompt for testing"

        # First, trigger the action to get the form
        data = {
            "action": "bulk_update_system_prompt",
            "_selected_action": selected_topics,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Update System Prompt")

        # Now submit the actual update
        data = {
            "action": "bulk_update_system_prompt",
            "_selected_action": selected_topics,
            "system_prompt": new_system_prompt,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Verify the system prompts were updated
        for topic_id in selected_topics:
            topic = Topic.objects.get(id=topic_id)
            self.assertEqual(topic.system_prompt, new_system_prompt)

    def test_bulk_context_type_update_action(self):
        """Test custom bulk action to update context types."""
        url = "/admin/rag/context/"

        # Test that we can access the context list
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Verify contexts are displayed
        for context in self.contexts:
            self.assertContains(response, context.name)

        # Test the bulk action form submission
        selected_contexts = [self.contexts[0].id, self.contexts[1].id]
        new_context_type = "MARKDOWN"

        # First, trigger the action to get the form
        data = {
            "action": "bulk_update_context_type",
            "_selected_action": selected_contexts,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Update Context Type")

        # Now submit the actual update
        data = {
            "action": "bulk_update_context_type",
            "_selected_action": selected_contexts,
            "context_type": new_context_type,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Verify the context types were updated
        for context_id in selected_contexts:
            context = Context.objects.get(id=context_id)
            self.assertEqual(context.context_type, new_context_type)

    def test_bulk_regenerate_embeddings_action(self):
        """Test custom bulk action to regenerate embeddings for context items."""
        url = "/admin/rag/contextitem/"

        # Test that we can access the context item list
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Verify context items are displayed
        for item in self.context_items[:5]:  # Check first 5
            self.assertContains(response, item.title)

        # Test the bulk action form submission
        selected_items = [self.context_items[0].id, self.context_items[1].id]

        # First, trigger the action to get the form
        data = {
            "action": "bulk_regenerate_embeddings",
            "_selected_action": selected_items,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Regenerate Embeddings")

        # Now submit the confirmation
        data = {
            "action": "bulk_regenerate_embeddings",
            "_selected_action": selected_items,
            "confirm": "yes",
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_bulk_move_to_context_action(self):
        """Test custom bulk action to move context items to another context."""
        url = "/admin/rag/contextitem/"

        # Test the bulk action form submission
        selected_items = [self.context_items[0].id, self.context_items[1].id]
        target_context = self.contexts[2]

        # First, trigger the action to get the form
        data = {
            "action": "bulk_move_to_context",
            "_selected_action": [str(item_id) for item_id in selected_items],
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Move Context Items")

        # Now submit the actual move
        data = {
            "action": "bulk_move_to_context",
            "_selected_action": [str(item_id) for item_id in selected_items],
            "context_id": str(target_context.id),
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Verify the items were moved to the target context
        for item_id in selected_items:
            item = ContextItem.objects.get(id=item_id)
            self.assertEqual(item.context, target_context)
