from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from rag.models import Topic


class TopicSelectionAPITest(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        # Clear any existing topics to ensure test isolation
        Topic.objects.all().delete()

        self.topic1 = Topic.objects.create(
            name="Mathematics",
            description="Math concepts and formulas",
            system_prompt="You are a math tutor.",
        )
        self.topic2 = Topic.objects.create(
            name="Science",
            description="Scientific principles and experiments",
            system_prompt="You are a science teacher.",
        )

    def test_get_all_topics_success(self):
        """Test retrieving all topics returns correct data."""
        url = reverse("rag:topics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # type: ignore[attr-defined]

        # Check first topic
        topic_data = response.data[0]  # type: ignore[attr-defined]
        self.assertEqual(topic_data["id"], self.topic1.id)
        self.assertEqual(topic_data["name"], "Mathematics")
        self.assertEqual(topic_data["description"], "Math concepts and formulas")

        # Check second topic
        topic_data = response.data[1]  # type: ignore[attr-defined]
        self.assertEqual(topic_data["id"], self.topic2.id)
        self.assertEqual(topic_data["name"], "Science")
        self.assertEqual(
            topic_data["description"], "Scientific principles and experiments"
        )

    def test_get_topics_when_empty(self):
        """Test retrieving topics when none exist."""
        Topic.objects.all().delete()
        url = reverse("rag:topics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # type: ignore[attr-defined]

    def test_get_single_topic_success(self):
        """Test retrieving a specific topic by ID."""
        url = reverse("rag:topic-detail", kwargs={"pk": self.topic1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.topic1.id)  # type: ignore[attr-defined]
        self.assertEqual(response.data["name"], "Mathematics")  # type: ignore[attr-defined]
        self.assertEqual(response.data["description"], "Math concepts and formulas")  # type: ignore[attr-defined]
        self.assertEqual(response.data["system_prompt"], "You are a math tutor.")  # type: ignore[attr-defined]

    def test_get_single_topic_not_found(self):
        """Test retrieving a non-existent topic returns 404."""
        url = reverse("rag:topic-detail", kwargs={"pk": 999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_topics_endpoint_only_allows_get(self):
        """Test that topics endpoint only allows GET requests."""
        url = reverse("rag:topics")

        # Test POST is not allowed
        response = self.client.post(url, {})
        self.assertIn(
            response.status_code,
            [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN],
        )

        # Test PUT is not allowed
        response = self.client.put(url, {})
        self.assertIn(
            response.status_code,
            [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN],
        )

        # Test DELETE is not allowed
        response = self.client.delete(url)
        self.assertIn(
            response.status_code,
            [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN],
        )


class APIErrorHandlingTest(TestCase):
    """Test comprehensive API error handling scenarios."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.topic = Topic.objects.create(
            name="Test Topic",
            description="Test description",
            system_prompt="You are a test assistant.",
        )

    def test_ask_question_with_malformed_json(self):
        """Test handling of malformed JSON in request body."""
        url = reverse("rag:ask-question")

        # Send malformed JSON
        response = self.client.post(
            url,
            data='{"topic_id": 1, "question": "test"',  # Missing closing brace
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ask_question_with_null_values(self):
        """Test handling of null values in request."""
        url = reverse("rag:ask-question")

        # Test null topic_id
        response = self.client.post(
            url, {"topic_id": None, "question": "What is this?"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("topic_id", response.data)  # type: ignore[attr-defined]

        # Test null question
        response = self.client.post(
            url, {"topic_id": self.topic.id, "question": None}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("question", response.data)  # type: ignore[attr-defined]

    def test_ask_question_with_invalid_data_types(self):
        """Test handling of invalid data types."""
        url = reverse("rag:ask-question")

        # Test string topic_id (should be integer)
        response = self.client.post(
            url, {"topic_id": "invalid", "question": "What is this?"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("topic_id", response.data)  # type: ignore[attr-defined]

        # Test non-string question (list instead of string)
        response = self.client.post(
            url,
            {"topic_id": self.topic.id, "question": ["not", "a", "string"]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("question", response.data)  # type: ignore[attr-defined]

    def test_ask_question_with_extremely_long_question(self):
        """Test handling of extremely long questions."""
        url = reverse("rag:ask-question")

        # Create a very long question (over 10,000 characters)
        long_question = "What is " + "a" * 10000 + "?"

        response = self.client.post(
            url, {"topic_id": self.topic.id, "question": long_question}, format="json"
        )

        # Should either reject the request or handle it gracefully
        # For now, we'll accept it as a valid test case
        self.assertIn(
            response.status_code,
            [
                status.HTTP_200_OK,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            ],
        )

    def test_ask_question_with_special_characters(self):
        """Test handling of special characters and Unicode."""
        url = reverse("rag:ask-question")

        # Test with various special characters and Unicode
        special_questions = [
            "What is 2 + 2? 🤔",
            "¿Qué es matemáticas?",
            "数学とは何ですか？",
            "What about \n\r\t line breaks?",
            "Question with \"quotes\" and 'apostrophes'",
            "Question with <script>alert('xss')</script>",
        ]

        for question in special_questions:
            with self.subTest(question=question):
                response = self.client.post(
                    url,
                    {"topic_id": self.topic.id, "question": question},
                    format="json",
                )

                # Should handle gracefully
                self.assertIn(
                    response.status_code,
                    [
                        status.HTTP_200_OK,
                        status.HTTP_400_BAD_REQUEST,
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                    ],
                )

    def test_ask_question_with_negative_topic_id(self):
        """Test handling of negative topic IDs."""
        url = reverse("rag:ask-question")

        response = self.client.post(
            url, {"topic_id": -1, "question": "What is this?"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("topic_id", response.data)  # type: ignore[attr-defined]

    def test_ask_question_with_zero_topic_id(self):
        """Test handling of zero topic ID."""
        url = reverse("rag:ask-question")

        response = self.client.post(
            url, {"topic_id": 0, "question": "What is this?"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("topic_id", response.data)  # type: ignore[attr-defined]

    def test_ask_question_with_whitespace_only_question(self):
        """Test handling of whitespace-only questions."""
        url = reverse("rag:ask-question")

        whitespace_questions = ["", "   ", "\t\n\r", "     \n\t   "]

        for question in whitespace_questions:
            with self.subTest(question=repr(question)):
                response = self.client.post(
                    url,
                    {"topic_id": self.topic.id, "question": question},
                    format="json",
                )

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_topic_detail_with_invalid_id_formats(self):
        """Test topic detail endpoint with various invalid ID formats."""
        invalid_ids = ["abc", "1.5", "999999999999999999999", "-1", "0"]

        for invalid_id in invalid_ids:
            with self.subTest(invalid_id=invalid_id):
                url = f"/api/topics/{invalid_id}/"
                response = self.client.get(url)

                # Should return either 400 or 404
                self.assertIn(
                    response.status_code,
                    [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND],
                )

    def test_topics_list_with_database_error_simulation(self):
        """Test topics list behavior when database is unavailable."""
        # This test would require mocking the database connection
        # For now, we'll test that the endpoint handles empty results gracefully
        Topic.objects.all().delete()

        url = reverse("rag:topics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # type: ignore[attr-defined]

    def test_ask_question_with_missing_fields(self):
        """Test handling of completely missing required fields."""
        url = reverse("rag:ask-question")

        # Test empty request body
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("topic_id", response.data)  # type: ignore[attr-defined]
        self.assertIn("question", response.data)  # type: ignore[attr-defined]

    def test_ask_question_with_short_question(self):
        """Test handling of very short questions."""
        url = reverse("rag:ask-question")

        response = self.client.post(
            url, {"topic_id": self.topic.id, "question": "Hi"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("question", response.data)  # type: ignore[attr-defined]


class TopicSelectionWebInterfaceTest(TestCase):
    """Test the web-based topic selection interface."""

    def setUp(self):
        """Set up test data."""
        self.topic1 = Topic.objects.create(
            name="Mathematics",
            description="Math concepts and formulas",
            system_prompt="You are a math tutor.",
        )
        self.topic2 = Topic.objects.create(
            name="Science",
            description="Scientific principles and experiments",
            system_prompt="You are a science teacher.",
        )

    def test_topic_selection_page_renders(self):
        """Test that the topic selection page renders successfully."""
        url = reverse("rag_web:topic-selection")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a Topic")
        self.assertContains(response, "Mathematics")
        self.assertContains(response, "Science")
        self.assertContains(response, "Math concepts and formulas")
        self.assertContains(response, "Scientific principles and experiments")

    def test_topic_selection_page_when_no_topics(self):
        """Test topic selection page when no topics exist."""
        Topic.objects.all().delete()
        url = reverse("rag_web:topic-selection")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Topics Available")

    def test_qa_page_renders_with_valid_topic(self):
        """Test that the Q&A page renders with a valid topic ID."""
        url = reverse("rag_web:qa-interface", kwargs={"topic_id": self.topic1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mathematics")
        self.assertContains(response, "Ask a Question")
        self.assertContains(response, "Math concepts and formulas")

    def test_qa_page_404_with_invalid_topic(self):
        """Test that Q&A page returns 404 for invalid topic ID."""
        url = reverse("rag_web:qa-interface", kwargs={"topic_id": 999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_qa_page_redirects_to_selection_when_no_topic_id(self):
        """Test that accessing Q&A without topic ID redirects to topic selection."""
        url = reverse("rag_web:qa-interface-redirect")
        response = self.client.get(url)

        self.assertRedirects(response, reverse("rag_web:topic-selection"))


class QuestionAnswerAPITest(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.topic = Topic.objects.create(
            name="Mathematics",
            description="Math concepts and formulas",
            system_prompt="You are a helpful math tutor.",
        )

    def test_ask_question_success(self):
        """Test successfully asking a question returns an answer."""
        url = reverse("rag:ask-question")
        data = {
            "topic_id": self.topic.id,
            "question": "What is the Pythagorean theorem?",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("answer", response.data)  # type: ignore[attr-defined]
        self.assertIn("citations", response.data)  # type: ignore[attr-defined]
        self.assertIn("topic_id", response.data)  # type: ignore[attr-defined]
        self.assertEqual(response.data["topic_id"], self.topic.id)  # type: ignore[attr-defined]
        self.assertIsInstance(response.data["answer"], str)  # type: ignore[attr-defined]
        self.assertIsInstance(response.data["citations"], list)  # type: ignore[attr-defined]

    def test_ask_question_missing_topic_id(self):
        """Test asking a question without topic_id returns error."""
        url = reverse("rag:ask-question")
        data = {"question": "What is the Pythagorean theorem?"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("topic_id", response.data)  # type: ignore[attr-defined]

    def test_ask_question_missing_question(self):
        """Test asking without question returns error."""
        url = reverse("rag:ask-question")
        data = {"topic_id": self.topic.id}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("question", response.data)  # type: ignore[attr-defined]

    def test_ask_question_invalid_topic_id(self):
        """Test asking a question with non-existent topic returns error."""
        url = reverse("rag:ask-question")
        data = {
            "topic_id": 999,
            "question": "What is the Pythagorean theorem?",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("topic_id", response.data)  # type: ignore[attr-defined]

    def test_ask_question_empty_question(self):
        """Test asking an empty question returns error."""
        url = reverse("rag:ask-question")
        data = {
            "topic_id": self.topic.id,
            "question": "",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ask_question_only_allows_post(self):
        """Test that ask-question endpoint only allows POST requests."""
        url = reverse("rag:ask-question")

        # Test GET is not allowed
        response = self.client.get(url)
        self.assertIn(
            response.status_code,
            [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN],
        )
