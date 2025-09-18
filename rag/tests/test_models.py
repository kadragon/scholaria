from django.core.exceptions import ValidationError
from django.test import TestCase

from rag.models import Context, ContextItem, Topic


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


class ContextModelTest(TestCase):
    def test_context_creation_with_required_fields(self):
        """Test creating a context with required fields."""
        context = Context.objects.create(
            name="Course Syllabus",
            description="University course syllabus and curriculum",
            context_type="PDF",
        )
        self.assertEqual(context.name, "Course Syllabus")
        self.assertEqual(
            context.description, "University course syllabus and curriculum"
        )
        self.assertEqual(context.context_type, "PDF")
        self.assertIsNotNone(context.id)
        self.assertIsNotNone(context.created_at)
        self.assertIsNotNone(context.updated_at)

    def test_context_name_required(self):
        """Test that context name is required."""
        with self.assertRaises(ValidationError):
            context = Context(description="Test description", context_type="PDF")
            context.full_clean()

    def test_context_description_required(self):
        """Test that context description is required."""
        with self.assertRaises(ValidationError):
            context = Context(name="Test Context", context_type="PDF")
            context.full_clean()

    def test_context_type_required(self):
        """Test that context type is required."""
        with self.assertRaises(ValidationError):
            context = Context(name="Test Context", description="Test description")
            context.full_clean()

    def test_context_type_choices(self):
        """Test that context type accepts valid choices."""
        valid_types = ["PDF", "FAQ", "MARKDOWN"]
        for context_type in valid_types:
            context = Context.objects.create(
                name=f"Test {context_type}",
                description=f"Test {context_type} description",
                context_type=context_type,
            )
            self.assertEqual(context.context_type, context_type)

    def test_context_type_invalid_choice(self):
        """Test that context type rejects invalid choices."""
        with self.assertRaises(ValidationError):
            context = Context(
                name="Test Context",
                description="Test description",
                context_type="INVALID",
            )
            context.full_clean()

    def test_context_string_representation(self):
        """Test the string representation of a context."""
        context = Context.objects.create(
            name="Course Syllabus",
            description="University course syllabus",
            context_type="PDF",
        )
        self.assertEqual(str(context), "Course Syllabus")

    def test_context_name_max_length(self):
        """Test context name max length validation."""
        long_name = "x" * 201  # Assuming max_length is 200
        with self.assertRaises(ValidationError):
            context = Context(
                name=long_name,
                description="Test description",
                context_type="PDF",
            )
            context.full_clean()


class ContextItemModelTest(TestCase):
    def setUp(self):
        """Set up test context for ContextItem tests."""
        self.context = Context.objects.create(
            name="Course Materials",
            description="University course materials",
            context_type="PDF",
        )

    def test_context_item_creation_with_required_fields(self):
        """Test creating a context item with required fields."""
        context_item = ContextItem.objects.create(
            title="Lecture 1: Introduction",
            content="This is the introduction lecture content...",
            context=self.context,
        )
        self.assertEqual(context_item.title, "Lecture 1: Introduction")
        self.assertEqual(
            context_item.content, "This is the introduction lecture content..."
        )
        self.assertEqual(context_item.context, self.context)
        self.assertIsNotNone(context_item.id)
        self.assertIsNotNone(context_item.created_at)
        self.assertIsNotNone(context_item.updated_at)

    def test_context_item_with_file_path(self):
        """Test creating a context item with file path."""
        context_item = ContextItem.objects.create(
            title="Course Syllabus",
            content="Course objectives and timeline...",
            context=self.context,
            file_path="documents/course_syllabus.pdf",
        )
        self.assertEqual(context_item.file_path, "documents/course_syllabus.pdf")

    def test_context_item_with_metadata(self):
        """Test creating a context item with metadata."""
        metadata = {"page_count": 10, "author": "Professor Smith"}
        context_item = ContextItem.objects.create(
            title="Research Paper",
            content="Abstract and introduction...",
            context=self.context,
            metadata=metadata,
        )
        self.assertEqual(context_item.metadata, metadata)

    def test_context_item_title_required(self):
        """Test that context item title is required."""
        with self.assertRaises(ValidationError):
            context_item = ContextItem(
                content="Test content",
                context=self.context,
            )
            context_item.full_clean()

    def test_context_item_content_required(self):
        """Test that context item content is required."""
        with self.assertRaises(ValidationError):
            context_item = ContextItem(
                title="Test Title",
                context=self.context,
            )
            context_item.full_clean()

    def test_context_item_context_required(self):
        """Test that context item context is required."""
        with self.assertRaises(ValidationError):
            context_item = ContextItem(
                title="Test Title",
                content="Test content",
            )
            context_item.full_clean()

    def test_context_item_string_representation(self):
        """Test the string representation of a context item."""
        context_item = ContextItem.objects.create(
            title="Lecture 1: Introduction",
            content="Introduction content",
            context=self.context,
        )
        self.assertEqual(str(context_item), "Lecture 1: Introduction")

    def test_context_item_title_max_length(self):
        """Test context item title max length validation."""
        long_title = "x" * 301  # Assuming max_length is 300
        with self.assertRaises(ValidationError):
            context_item = ContextItem(
                title=long_title,
                content="Test content",
                context=self.context,
            )
            context_item.full_clean()

    def test_context_item_ordering(self):
        """Test context items are ordered by creation date."""
        item1 = ContextItem.objects.create(
            title="First Item",
            content="First content",
            context=self.context,
        )
        item2 = ContextItem.objects.create(
            title="Second Item",
            content="Second content",
            context=self.context,
        )
        items = list(ContextItem.objects.all())
        self.assertEqual(items[0], item1)
        self.assertEqual(items[1], item2)
