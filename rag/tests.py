from django.core.exceptions import ValidationError
from django.test import TestCase

from rag.models import Topic


class TopicModelTest(TestCase):
    def test_topic_creation_with_required_fields(self):
        """Test creating a topic with required fields."""
        topic = Topic.objects.create(
            name="Math Fundamentals",
            description="Basic mathematics concepts and principles",
        )
        self.assertEqual(topic.name, "Math Fundamentals")
        self.assertEqual(topic.description, "Basic mathematics concepts and principles")
        self.assertIsNotNone(topic.id)
        self.assertIsNotNone(topic.created_at)
        self.assertIsNotNone(topic.updated_at)

    def test_topic_creation_with_system_prompt(self):
        """Test creating a topic with system prompt."""
        system_prompt = (
            "You are a math tutor. Answer questions about basic mathematics."
        )
        topic = Topic.objects.create(
            name="Math Fundamentals",
            description="Basic mathematics concepts and principles",
            system_prompt=system_prompt,
        )
        self.assertEqual(topic.system_prompt, system_prompt)

    def test_topic_name_required(self):
        """Test that topic name is required."""
        with self.assertRaises(ValidationError):
            topic = Topic(description="Test description")
            topic.full_clean()

    def test_topic_description_required(self):
        """Test that topic description is required."""
        with self.assertRaises(ValidationError):
            topic = Topic(name="Test Topic")
            topic.full_clean()

    def test_topic_string_representation(self):
        """Test the string representation of a topic."""
        topic = Topic.objects.create(
            name="Math Fundamentals", description="Basic mathematics concepts"
        )
        self.assertEqual(str(topic), "Math Fundamentals")

    def test_topic_name_max_length(self):
        """Test topic name max length validation."""
        long_name = "x" * 201  # Assuming max_length is 200
        with self.assertRaises(ValidationError):
            topic = Topic(name=long_name, description="Test description")
            topic.full_clean()
