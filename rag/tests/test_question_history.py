from django.core.exceptions import ValidationError
from django.test import TestCase

from rag.models import QuestionHistory, Topic


class QuestionHistoryModelTest(TestCase):
    """Test case for QuestionHistory model functionality."""

    def setUp(self):
        """Set up test data."""
        self.topic = Topic.objects.create(
            name="Test Topic",
            description="Test description",
            system_prompt="You are a helpful assistant.",
        )

    def test_question_history_creation_success(self):
        """Test that QuestionHistory can be created with valid data."""
        history = QuestionHistory.objects.create(
            topic=self.topic,
            question="What is machine learning?",
            answer="Machine learning is a subset of artificial intelligence.",
            session_id="test-session-123",
        )

        self.assertEqual(history.topic, self.topic)
        self.assertEqual(history.question, "What is machine learning?")
        self.assertEqual(
            history.answer, "Machine learning is a subset of artificial intelligence."
        )
        self.assertEqual(history.session_id, "test-session-123")
        self.assertFalse(history.is_favorited)
        self.assertIsNotNone(history.created_at)

    def test_question_history_validation_requires_topic(self):
        """Test that QuestionHistory requires a topic."""
        history = QuestionHistory(
            question="What is AI?",
            answer="AI is artificial intelligence.",
            session_id="test-session",
        )

        with self.assertRaises(ValidationError) as cm:
            history.full_clean()

        self.assertIn("topic", cm.exception.message_dict)

    def test_question_history_validation_requires_question(self):
        """Test that QuestionHistory requires a question."""
        history = QuestionHistory(
            topic=self.topic, answer="This is an answer.", session_id="test-session"
        )

        with self.assertRaises(ValidationError) as cm:
            history.full_clean()

        self.assertIn("question", cm.exception.message_dict)

    def test_question_history_validation_requires_answer(self):
        """Test that QuestionHistory requires an answer."""
        history = QuestionHistory(
            topic=self.topic, question="What is this?", session_id="test-session"
        )

        with self.assertRaises(ValidationError) as cm:
            history.full_clean()

        self.assertIn("answer", cm.exception.message_dict)

    def test_question_history_validation_requires_session_id(self):
        """Test that QuestionHistory requires a session_id."""
        history = QuestionHistory(
            topic=self.topic, question="What is this?", answer="This is an answer."
        )

        with self.assertRaises(ValidationError) as cm:
            history.full_clean()

        self.assertIn("session_id", cm.exception.message_dict)

    def test_question_history_favorited_functionality(self):
        """Test that questions can be favorited and unfavorited."""
        history = QuestionHistory.objects.create(
            topic=self.topic,
            question="What is deep learning?",
            answer="Deep learning is a subset of machine learning.",
            session_id="test-session",
        )

        # Initially not favorited
        self.assertFalse(history.is_favorited)

        # Favorite the question
        history.is_favorited = True
        history.save()
        history.refresh_from_db()
        self.assertTrue(history.is_favorited)

        # Unfavorite the question
        history.is_favorited = False
        history.save()
        history.refresh_from_db()
        self.assertFalse(history.is_favorited)

    def test_question_history_ordering(self):
        """Test that QuestionHistory is ordered by creation date (newest first)."""
        # Create questions at different times
        history1 = QuestionHistory.objects.create(
            topic=self.topic,
            question="First question",
            answer="First answer",
            session_id="session-1",
        )

        # Simulate time passing
        history2 = QuestionHistory.objects.create(
            topic=self.topic,
            question="Second question",
            answer="Second answer",
            session_id="session-2",
        )

        # Get all histories - should be ordered newest first
        histories = list(QuestionHistory.objects.all())
        self.assertEqual(histories[0], history2)  # Newest first
        self.assertEqual(histories[1], history1)

    def test_question_history_str_representation(self):
        """Test the string representation of QuestionHistory."""
        history = QuestionHistory.objects.create(
            topic=self.topic,
            question="What is neural network?",
            answer="A neural network is a computing system.",
            session_id="test-session",
        )

        expected_str = "What is neural network? (Test Topic)"
        self.assertEqual(str(history), expected_str)

    def test_question_history_get_by_session(self):
        """Test querying QuestionHistory by session_id."""
        # Create questions for different sessions
        QuestionHistory.objects.create(
            topic=self.topic,
            question="Session 1 Question 1",
            answer="Session 1 Answer 1",
            session_id="session-1",
        )

        QuestionHistory.objects.create(
            topic=self.topic,
            question="Session 1 Question 2",
            answer="Session 1 Answer 2",
            session_id="session-1",
        )

        QuestionHistory.objects.create(
            topic=self.topic,
            question="Session 2 Question 1",
            answer="Session 2 Answer 1",
            session_id="session-2",
        )

        # Query by session
        session_1_histories = QuestionHistory.objects.filter(session_id="session-1")
        session_2_histories = QuestionHistory.objects.filter(session_id="session-2")

        self.assertEqual(session_1_histories.count(), 2)
        self.assertEqual(session_2_histories.count(), 1)

    def test_question_history_get_favorites(self):
        """Test querying favorited QuestionHistory items."""
        # Create some favorited and non-favorited questions
        fav1 = QuestionHistory.objects.create(
            topic=self.topic,
            question="Favorited question 1",
            answer="Favorited answer 1",
            session_id="session-1",
            is_favorited=True,
        )

        QuestionHistory.objects.create(
            topic=self.topic,
            question="Regular question",
            answer="Regular answer",
            session_id="session-1",
            is_favorited=False,
        )

        fav2 = QuestionHistory.objects.create(
            topic=self.topic,
            question="Favorited question 2",
            answer="Favorited answer 2",
            session_id="session-2",
            is_favorited=True,
        )

        # Query favorites
        favorites = QuestionHistory.objects.filter(is_favorited=True)

        self.assertEqual(favorites.count(), 2)
        self.assertIn(fav1, favorites)
        self.assertIn(fav2, favorites)
