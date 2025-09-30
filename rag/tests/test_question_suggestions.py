"""
Tests for question suggestion functionality based on topic content.
"""

import json

from django.test import TestCase
from django.urls import reverse

from rag.models import Context, ContextItem, Topic


class QuestionSuggestionsTestCase(TestCase):
    """Test case for question suggestions based on topic content."""

    def setUp(self):
        """Set up test data."""
        self.topic = Topic.objects.create(
            name="Mathematics",
            description="Mathematical concepts and problem solving",
            system_prompt="You are a helpful math tutor.",
        )

        self.context = Context.objects.create(
            name="Algebra Basics",
            description="Introduction to algebraic concepts",
            context_type="MARKDOWN",
            processing_status="COMPLETED",
            original_content="Linear equations are mathematical statements of equality between two expressions.",
        )

        self.context_item = ContextItem.objects.create(
            title="Linear Equations",
            content="Linear equations are mathematical statements of equality between two expressions. They can be written in the form ax + b = c, where a, b, and c are constants.",
            context=self.context,
        )

        self.topic.contexts.add(self.context)

    def test_generate_questions_from_context_item(self):
        """Test that questions can be generated from a context item."""
        from rag.services.question_suggestions import QuestionSuggestionService

        service = QuestionSuggestionService()

        # Should generate relevant questions from the content
        questions = service.generate_questions_from_content(self.context_item.content)

        self.assertIsInstance(questions, list)
        self.assertGreater(len(questions), 0)
        self.assertLessEqual(len(questions), 5)  # Should limit to reasonable number

        # Each question should be a non-empty string
        for question in questions:
            self.assertIsInstance(question, str)
            self.assertGreater(len(question.strip()), 0)

    def test_get_topic_suggestions(self):
        """Test getting question suggestions for a topic."""
        from rag.services.question_suggestions import QuestionSuggestionService

        service = QuestionSuggestionService()
        suggestions = service.get_topic_suggestions(self.topic.id)

        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)

        # Should contain questions related to the topic content
        for suggestion in suggestions:
            self.assertIsInstance(suggestion, str)
            self.assertGreater(len(suggestion.strip()), 0)

    def test_question_suggestions_api_endpoint(self):
        """Test the API endpoint for question suggestions."""
        url = f"/api/topics/{self.topic.id}/suggestions/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertIn("suggestions", data)
        self.assertIsInstance(data["suggestions"], list)
        self.assertGreater(len(data["suggestions"]), 0)

    def test_question_suggestions_api_invalid_topic(self):
        """Test API endpoint with invalid topic ID."""
        url = "/api/topics/999/suggestions/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_qa_interface_includes_suggestions_ui(self):
        """Test that Q&A interface includes question suggestions UI."""
        response = self.client.get(
            reverse("rag_web:qa-interface", kwargs={"topic_id": self.topic.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "question-suggestions")
        self.assertContains(response, "suggestion-item")
        self.assertContains(response, "suggestionsContainer")

    def test_suggestions_ui_with_no_context(self):
        """Test suggestions UI when topic has no context."""
        empty_topic = Topic.objects.create(
            name="Empty Topic",
            description="Topic with no context",
            system_prompt="Test prompt",
        )

        response = self.client.get(
            reverse("rag_web:qa-interface", kwargs={"topic_id": empty_topic.id})
        )

        self.assertEqual(response.status_code, 200)
        # Should still include suggestions container but may be empty
        self.assertContains(response, "question-suggestions")

    def test_pattern_based_question_generation(self):
        """Test pattern-based question generation without external LLM."""
        from rag.services.question_suggestions import QuestionSuggestionService

        service = QuestionSuggestionService()

        # Test content with recognizable patterns
        test_content = "Machine Learning is a subset of artificial intelligence. It involves algorithms that learn from data."
        questions = service.generate_questions_from_content(test_content)

        self.assertIsInstance(questions, list)
        self.assertGreater(len(questions), 0)

        # Should generate relevant questions based on patterns
        question_text = " ".join(questions).lower()
        self.assertTrue(
            any(word in question_text for word in ["machine", "learning", "algorithm"])
        )

    def test_question_suggestions_caching(self):
        """Test that question suggestions are cached appropriately."""
        from rag.services.question_suggestions import QuestionSuggestionService

        service = QuestionSuggestionService()

        # First call should generate suggestions
        suggestions1 = service.get_topic_suggestions(self.topic.id)

        # Second call should return cached results (if caching is implemented)
        suggestions2 = service.get_topic_suggestions(self.topic.id)

        self.assertEqual(suggestions1, suggestions2)

    def test_suggestions_limit_and_quality(self):
        """Test that suggestions are limited in number and have good quality."""
        from rag.services.question_suggestions import QuestionSuggestionService

        service = QuestionSuggestionService()
        suggestions = service.get_topic_suggestions(self.topic.id)

        # Should limit number of suggestions
        self.assertLessEqual(len(suggestions), 8)

        # Each suggestion should be a proper question
        for suggestion in suggestions:
            self.assertTrue(suggestion.strip().endswith("?"))
            self.assertGreater(len(suggestion.strip()), 10)  # Minimum meaningful length
