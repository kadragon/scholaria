"""
Tests for enhanced chunk management functionality.
"""

import json

from django.contrib.admin.sites import site
from django.contrib.auth.models import User
from django.test import TestCase

from rag.admin import ContextAdmin
from rag.models import Context, ContextItem, Topic


class ChunkManagementTestCase(TestCase):
    """Test case for enhanced chunk management features."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_superuser(
            username="admin", email="admin@test.com", password="admin123"
        )

        self.topic = Topic.objects.create(
            name="Test Topic",
            description="Test topic for chunk management",
            system_prompt="You are a helpful assistant.",
        )

        self.context = Context.objects.create(
            name="Test Context",
            description="Test context with chunks",
            context_type="MARKDOWN",
            processing_status="COMPLETED",
            original_content="This is the original content of the context.",
        )

        # Create multiple chunks for testing
        self.chunks = []
        for i in range(5):
            chunk = ContextItem.objects.create(
                title=f"Chunk {i + 1}",
                content=f"This is content for chunk {i + 1}. It contains information about topic {i + 1}.",
                context=self.context,
            )
            self.chunks.append(chunk)

        self.context.update_chunk_count()

    def test_context_admin_has_chunk_preview(self):
        """Test that context admin includes chunk preview functionality."""

        admin_instance = ContextAdmin(Context, site)

        # Should have methods for chunk management
        self.assertTrue(hasattr(admin_instance, "get_chunk_preview"))
        self.assertTrue(hasattr(admin_instance, "get_chunk_statistics"))

    def test_chunk_preview_api_endpoint(self):
        """Test API endpoint for chunk preview."""
        self.client.force_login(self.user)

        url = f"/api/contexts/{self.context.pk}/chunks/preview/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertIn("chunks", data)
        self.assertIn("total_count", data)
        self.assertIn("context_info", data)

        # Should have chunk data
        chunks = data["chunks"]
        self.assertGreater(len(chunks), 0)

        # Each chunk should have required fields
        for chunk in chunks:
            self.assertIn("id", chunk)
            self.assertIn("title", chunk)
            self.assertIn("content_preview", chunk)
            self.assertIn("content_length", chunk)
            self.assertIn("created_at", chunk)

    def test_chunk_editing_functionality(self):
        """Test that chunks can be edited through admin interface."""
        self.client.force_login(self.user)

        # Test accessing chunk through context admin (inline editing)
        context_url = f"/admin/rag/context/{self.context.pk}/change/"

        response = self.client.get(context_url)
        self.assertEqual(response.status_code, 200)

        # Should contain chunk editing form through inline
        self.assertContains(response, "field-chunk_preview")
        self.assertContains(response, "field-title")

    def test_chunk_reordering_api(self):
        """Test API endpoint for chunk reordering."""
        self.client.force_login(self.user)

        # Test reordering chunks
        new_order = [chunk.id for chunk in reversed(self.chunks)]

        url = f"/api/contexts/{self.context.pk}/chunks/reorder/"
        response = self.client.post(
            url,
            data=json.dumps({"chunk_order": new_order}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertTrue(data["success"])

    def test_chunk_bulk_operations(self):
        """Test bulk operations on chunks."""
        self.client.force_login(self.user)

        chunk_ids = [chunk.id for chunk in self.chunks[:3]]

        # Test bulk delete
        url = f"/api/contexts/{self.context.pk}/chunks/bulk/"
        response = self.client.delete(
            url,
            data=json.dumps({"chunk_ids": chunk_ids, "operation": "delete"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertTrue(data["success"])
        self.assertEqual(data["affected_count"], 3)

    def test_processing_status_updates(self):
        """Test real-time processing status updates."""
        self.client.force_login(self.user)

        # Update processing status
        self.context.processing_status = "PROCESSING"
        self.context.save()

        url = f"/api/contexts/{self.context.pk}/status/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data["processing_status"], "PROCESSING")
        self.assertIn("last_updated", data)

    def test_chunk_search_and_filter(self):
        """Test chunk search and filtering functionality."""
        self.client.force_login(self.user)

        url = f"/api/contexts/{self.context.pk}/chunks/search/"

        # Test search by content
        response = self.client.get(url, {"q": "content", "limit": "10"})
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertIn("chunks", data)
        self.assertGreater(len(data["chunks"]), 0)

    def test_chunk_validation_rules(self):
        """Test chunk validation and quality rules."""
        self.client.force_login(self.user)

        # Test chunk validation
        url = f"/api/contexts/{self.context.pk}/chunks/validate/"
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertIn("validation_results", data)
        self.assertIn("issues_found", data)

    def test_chunk_statistics_display(self):
        """Test chunk statistics display in admin."""
        self.client.force_login(self.user)

        # Admin change view should show chunk statistics
        url = f"/admin/rag/context/{self.context.pk}/change/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # Should show chunk count somewhere in the admin interface
        self.assertContains(response, f"{self.context.chunk_count}")

    def test_chunk_content_preview_truncation(self):
        """Test that chunk content is properly truncated in previews."""
        # Create a chunk with very long content
        long_content = "A" * 2000  # 2000 characters
        long_chunk = ContextItem.objects.create(
            title="Long Chunk", content=long_content, context=self.context
        )

        self.client.force_login(self.user)

        url = f"/api/contexts/{self.context.pk}/chunks/preview/"
        response = self.client.get(url)

        data = json.loads(response.content)

        # Find the long chunk in response
        long_chunk_data = None
        for chunk in data["chunks"]:
            if chunk["id"] == long_chunk.id:
                long_chunk_data = chunk
                break

        self.assertIsNotNone(long_chunk_data)
        # Preview should be truncated
        if long_chunk_data is not None:
            self.assertLess(len(long_chunk_data["content_preview"]), 500)
            # Should indicate truncation
            self.assertTrue(long_chunk_data["content_preview"].endswith("..."))

    def test_chunk_management_permissions(self):
        """Test that chunk management requires proper permissions."""
        # Test without login
        url = f"/api/contexts/{self.context.pk}/chunks/preview/"
        response = self.client.get(url)

        # Should require authentication (401 or 403)
        self.assertIn(response.status_code, [401, 403])  # Unauthorized or forbidden

        # Test with regular user (authenticated but not admin)
        regular_user = User.objects.create_user(
            username="regular", email="regular@test.com", password="regular123"
        )
        self.client.force_login(regular_user)

        response = self.client.get(url)
        # For now, authenticated users can access (may need to add admin permission later)
        self.assertEqual(response.status_code, 200)
