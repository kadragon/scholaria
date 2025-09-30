from django.test import TestCase
from django.urls import reverse

from rag.models import Topic


class MobileOptimizationTestCase(TestCase):
    """Test case for mobile responsiveness and touch optimization."""

    def setUp(self):
        """Set up test data."""
        self.topic = Topic.objects.create(
            name="Test Topic",
            description="Test description",
            system_prompt="You are a helpful assistant.",
        )

    def test_qa_interface_has_viewport_meta_tag(self):
        """Test that Q&A interface includes proper viewport meta tag."""
        response = self.client.get(
            reverse("rag_web:qa-interface", kwargs={"topic_id": self.topic.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="viewport"')
        self.assertContains(response, "width=device-width")
        self.assertContains(response, "initial-scale=1.0")

    def test_qa_interface_includes_touch_optimized_css(self):
        """Test that Q&A interface includes CSS for touch optimization."""
        response = self.client.get(
            reverse("rag_web:qa-interface", kwargs={"topic_id": self.topic.id})
        )

        self.assertEqual(response.status_code, 200)
        # Check for touch-specific CSS classes and properties
        self.assertContains(response, "touch-action")
        self.assertContains(response, "mobile-optimized")
        self.assertContains(response, "touch-target")

    def test_qa_interface_includes_swipe_gesture_support(self):
        """Test that Q&A interface includes JavaScript for swipe gestures."""
        response = self.client.get(
            reverse("rag_web:qa-interface", kwargs={"topic_id": self.topic.id})
        )

        self.assertEqual(response.status_code, 200)
        # Check for swipe-related JavaScript functionality
        self.assertContains(response, "handleSwipe")
        self.assertContains(response, "touchStart")
        self.assertContains(response, "touchEnd")

    def test_qa_interface_includes_mobile_layout_classes(self):
        """Test that Q&A interface includes mobile-specific layout classes."""
        response = self.client.get(
            reverse("rag_web:qa-interface", kwargs={"topic_id": self.topic.id})
        )

        self.assertEqual(response.status_code, 200)
        # Check for mobile layout optimizations
        self.assertContains(response, "mobile-container")
        self.assertContains(response, "mobile-form")
        self.assertContains(response, "mobile-button")

    def test_qa_interface_includes_haptic_feedback_support(self):
        """Test that Q&A interface includes haptic feedback for mobile."""
        response = self.client.get(
            reverse("rag_web:qa-interface", kwargs={"topic_id": self.topic.id})
        )

        self.assertEqual(response.status_code, 200)
        # Check for haptic feedback functionality
        self.assertContains(response, "navigator.vibrate")
        self.assertContains(response, "hapticFeedback")

    def test_qa_interface_includes_mobile_typography_classes(self):
        """Test that Q&A interface includes mobile-optimized typography."""
        response = self.client.get(
            reverse("rag_web:qa-interface", kwargs={"topic_id": self.topic.id})
        )

        self.assertEqual(response.status_code, 200)
        # Check for mobile typography optimizations
        self.assertContains(response, "mobile-text")
        self.assertContains(response, "large-touch-target")

    def test_topic_selection_has_mobile_grid_layout(self):
        """Test that topic selection page has mobile-optimized grid."""
        response = self.client.get(reverse("rag_web:topic-selection"))

        self.assertEqual(response.status_code, 200)
        # Check for mobile grid optimizations
        self.assertContains(response, "mobile-grid")
        self.assertContains(response, "touch-card")
