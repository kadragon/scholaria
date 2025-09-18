from django.contrib import admin
from django.contrib.auth.models import User
from django.test import Client, TestCase

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
        expected_fields = ["title", "context", "file_path", "created_at"]
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
        expected_fields = ["created_at", "updated_at"]
        self.assertEqual(list(contextitem_admin.readonly_fields), expected_fields)
