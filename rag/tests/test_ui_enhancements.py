from django.test import TestCase
from django.urls import reverse

from rag.models import Topic


class UIEnhancementTestCase(TestCase):
    """Test case for Q&A interface UI enhancements."""

    def setUp(self):
        """Set up test data."""
        # Clear existing topics
        Topic.objects.all().delete()

        self.topic = Topic.objects.create(
            name="Test Topic",
            description="Test description",
            system_prompt="You are a helpful assistant.",
        )

    def test_qa_interface_contains_typing_indicator_element(self):
        """Test that Q&A interface template includes typing indicator element."""
        response = self.client.get(
            reverse("rag_web:qa-interface", kwargs={"topic_id": self.topic.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="typingIndicator"')
        self.assertContains(response, "typing-indicator")

    def test_qa_interface_contains_enhanced_loading_elements(self):
        """Test that Q&A interface includes enhanced loading animation elements."""
        response = self.client.get(
            reverse("rag_web:qa-interface", kwargs={"topic_id": self.topic.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="enhancedLoadingDiv"')
        self.assertContains(response, "loading-dots")
        self.assertContains(response, "loading-message")

    def test_qa_interface_includes_animation_css(self):
        """Test that Q&A interface includes CSS for smooth animations."""
        response = self.client.get(
            reverse("rag_web:qa-interface", kwargs={"topic_id": self.topic.id})
        )

        self.assertEqual(response.status_code, 200)
        # Check for animation-related CSS classes
        self.assertContains(response, "fade-in")
        self.assertContains(response, "transition")
        self.assertContains(response, "typing-indicator")

    def test_qa_interface_includes_typing_detection_javascript(self):
        """Test that Q&A interface includes JavaScript for typing detection."""
        response = self.client.get(
            reverse("rag_web:qa-interface", kwargs={"topic_id": self.topic.id})
        )

        self.assertEqual(response.status_code, 200)
        # Check for typing-related JavaScript functionality
        self.assertContains(response, "typingTimer")
        self.assertContains(response, "showTypingIndicator")
        self.assertContains(response, "hideTypingIndicator")
