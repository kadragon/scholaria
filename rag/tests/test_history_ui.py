from django.test import TestCase
from django.urls import reverse

from rag.models import QuestionHistory, Topic


class HistoryUITestCase(TestCase):
    """Test case for question history and favorites UI functionality."""

    def setUp(self):
        """Set up test data."""
        self.topic = Topic.objects.create(
            name="Test Topic",
            description="Test description",
            system_prompt="You are a helpful assistant.",
        )

        # Create some test history
        self.history1 = QuestionHistory.objects.create(
            topic=self.topic,
            question="What is machine learning?",
            answer="Machine learning is a subset of AI.",
            session_id="test-session-1",
            is_favorited=True,
        )

        self.history2 = QuestionHistory.objects.create(
            topic=self.topic,
            question="What is deep learning?",
            answer="Deep learning is a subset of machine learning.",
            session_id="test-session-1",
            is_favorited=False,
        )

    def test_qa_interface_contains_history_sidebar_elements(self):
        """Test that Q&A interface includes history sidebar elements."""
        response = self.client.get(
            reverse("rag_web:qa-interface", kwargs={"topic_id": self.topic.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="historySidebar"')
        self.assertContains(response, "history-sidebar")
        self.assertContains(response, "history-toggle-btn")

    def test_qa_interface_contains_history_controls(self):
        """Test that Q&A interface includes history control elements."""
        response = self.client.get(
            reverse("rag_web:qa-interface", kwargs={"topic_id": self.topic.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "history-list")
        self.assertContains(response, "favorites-list")
        self.assertContains(response, "clear-history-btn")

    def test_qa_interface_includes_history_javascript(self):
        """Test that Q&A interface includes JavaScript for history functionality."""
        response = self.client.get(
            reverse("rag_web:qa-interface", kwargs={"topic_id": self.topic.id})
        )

        self.assertEqual(response.status_code, 200)
        # Check for history-related JavaScript functionality
        self.assertContains(response, "toggleHistorySidebar")
        self.assertContains(response, "addToHistory")
        self.assertContains(response, "toggleFavorite")
        self.assertContains(response, "loadQuestionHistory")

    def test_qa_interface_includes_history_css(self):
        """Test that Q&A interface includes CSS for history styling."""
        response = self.client.get(
            reverse("rag_web:qa-interface", kwargs={"topic_id": self.topic.id})
        )

        self.assertEqual(response.status_code, 200)
        # Check for history-related CSS classes
        self.assertContains(response, "history-sidebar")
        self.assertContains(response, "history-item")
        self.assertContains(response, "favorite-btn")
        self.assertContains(response, "sidebar-open")

    def test_qa_interface_includes_favorite_icons(self):
        """Test that Q&A interface includes favorite star icons."""
        response = self.client.get(
            reverse("rag_web:qa-interface", kwargs={"topic_id": self.topic.id})
        )

        self.assertEqual(response.status_code, 200)
        # Check for star icons for favorites
        self.assertContains(response, "★")  # Filled star
        self.assertContains(response, "☆")  # Empty star
