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
