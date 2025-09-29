"""
Tests for question history API endpoints.
"""

import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from rag.models import QuestionHistory, Topic


class QuestionHistoryAPITest(TestCase):
    """Test question history API functionality."""

    def setUp(self) -> None:
        """Set up test data."""
        self.client = APIClient()
        self.topic = Topic.objects.create(name="Test Topic", description="A test topic")

    def test_save_question_history(self) -> None:
        """Test saving question history via API."""
        data = {
            "question": "What is neural network?",
            "answer": "A neural network is a computing system.",
            "topic_id": self.topic.pk,
            "session_id": "test-session-new",
        }

        response = self.client.post(
            reverse("api_save_question_history"),
            data=json.dumps(data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        self.assertEqual(response_data["success"], True)
        self.assertIn("id", response_data)

        # Verify in database
        history = QuestionHistory.objects.get(pk=response_data["id"])
        self.assertEqual(history.question, "What is neural network?")
        self.assertEqual(history.answer, "A neural network is a computing system.")
        self.assertEqual(history.session_id, "test-session-new")
        self.assertFalse(history.is_favorited)

    def test_get_question_history(self) -> None:
        """Test retrieving question history via API."""
        # Create test history
        QuestionHistory.objects.create(
            question="Test question?",
            answer="Test answer.",
            topic=self.topic,
            session_id="test-session-get",
        )

        response = self.client.get(
            reverse("api_question_history"),
            {"topic_id": self.topic.pk, "session_id": "test-session-get"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertIn("history", response_data)

        histories = response_data["history"]
        self.assertEqual(len(histories), 1)
        self.assertEqual(histories[0]["question"], "Test question?")
        self.assertEqual(histories[0]["answer"], "Test answer.")

    def test_toggle_favorite(self) -> None:
        """Test toggling favorite status via API."""
        history = QuestionHistory.objects.create(
            question="Favorite test?",
            answer="Favorite answer.",
            topic=self.topic,
            session_id="test-session-fav",
        )

        # Toggle to favorite
        response = self.client.post(
            reverse("api_toggle_favorite", kwargs={"history_id": history.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["success"], True)
        self.assertTrue(response_data["is_favorited"])

        # Verify in database
        history.refresh_from_db()
        self.assertTrue(history.is_favorited)

    def test_get_favorites(self) -> None:
        """Test retrieving favorites via API."""
        # Create favorite history
        QuestionHistory.objects.create(
            question="Favorite question?",
            answer="Favorite answer.",
            topic=self.topic,
            session_id="test-session-favorites",
            is_favorited=True,
        )

        # Create non-favorite history
        QuestionHistory.objects.create(
            question="Regular question?",
            answer="Regular answer.",
            topic=self.topic,
            session_id="test-session-favorites",
            is_favorited=False,
        )

        response = self.client.get(
            reverse("api_favorites"), {"topic_id": self.topic.pk}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertIn("favorites", response_data)

        favorites = response_data["favorites"]
        self.assertEqual(len(favorites), 1)
        self.assertEqual(favorites[0]["question"], "Favorite question?")
        self.assertTrue(favorites[0]["is_favorited"])
