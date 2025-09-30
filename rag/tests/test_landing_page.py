from django.test import TestCase
from django.urls import reverse

from rag.models import Topic


class LandingPageTestCase(TestCase):
    """Test case for improved landing page and navigation."""

    def setUp(self):
        """Set up test data."""
        self.topic1 = Topic.objects.create(
            name="Mathematics",
            description="Explore mathematical concepts, formulas, and problem-solving techniques",
            system_prompt="You are a helpful math tutor.",
        )

        self.topic2 = Topic.objects.create(
            name="Science",
            description="Dive into scientific principles, experiments, and discoveries",
            system_prompt="You are a science teacher.",
        )

    def test_landing_page_includes_hero_section(self):
        """Test that landing page includes a compelling hero section."""
        response = self.client.get(reverse("rag_web:topic-selection"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "hero-section")
        self.assertContains(response, "hero-title")
        self.assertContains(response, "hero-subtitle")
        self.assertContains(response, "cta-button")

    def test_landing_page_includes_navigation_menu(self):
        """Test that landing page includes navigation menu."""
        response = self.client.get(reverse("rag_web:topic-selection"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "nav-menu")
        self.assertContains(response, "nav-brand")
        self.assertContains(response, "nav-links")

    def test_landing_page_includes_breadcrumb_navigation(self):
        """Test that landing page includes breadcrumb navigation."""
        response = self.client.get(reverse("rag_web:topic-selection"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "breadcrumb")
        self.assertContains(response, "breadcrumb-item")

    def test_landing_page_includes_enhanced_topic_cards(self):
        """Test that landing page includes enhanced topic cards with icons and stats."""
        response = self.client.get(reverse("rag_web:topic-selection"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "topic-card-enhanced")
        self.assertContains(response, "topic-icon")
        self.assertContains(response, "topic-stats")
        self.assertContains(response, "card-hover-effect")

    def test_landing_page_includes_feature_highlights(self):
        """Test that landing page includes feature highlights section."""
        response = self.client.get(reverse("rag_web:topic-selection"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "features-section")
        self.assertContains(response, "feature-item")
        self.assertContains(response, "feature-icon")

    def test_landing_page_includes_footer_section(self):
        """Test that landing page includes informative footer."""
        response = self.client.get(reverse("rag_web:topic-selection"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "footer-section")
        self.assertContains(response, "footer-content")

    def test_qa_interface_includes_breadcrumb_navigation(self):
        """Test that Q&A interface includes breadcrumb navigation."""
        response = self.client.get(
            reverse("rag_web:qa-interface", kwargs={"topic_id": self.topic1.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "breadcrumb")
        self.assertContains(response, "breadcrumb-home")
        self.assertContains(response, "breadcrumb-current")

    def test_landing_page_includes_search_functionality(self):
        """Test that landing page includes topic search functionality."""
        response = self.client.get(reverse("rag_web:topic-selection"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "topic-search")
        self.assertContains(response, "search-input")
        self.assertContains(response, "search-filter")

    def test_landing_page_includes_animation_classes(self):
        """Test that landing page includes CSS animation classes."""
        response = self.client.get(reverse("rag_web:topic-selection"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "fade-in-up")
        self.assertContains(response, "stagger-animation")
        self.assertContains(response, "parallax-effect")
