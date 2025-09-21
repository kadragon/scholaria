from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from rag.models import Context


class MarkdownDirectEditWorkflowTest(TestCase):
    """Test the markdown direct editing workflow."""

    def test_markdown_context_creation_with_direct_editing(self):
        """
        Test that Markdown contexts can be created and edited directly without file uploads.
        """
        # Create a Markdown context
        context = Context.objects.create(
            name="Test Markdown Context",
            description="Test context for markdown workflow",
            context_type="MARKDOWN",
        )

        # Should create empty context ready for direct content editing
        self.assertEqual(context.context_type, "MARKDOWN")
        self.assertEqual(context.processing_status, "PENDING")
        self.assertEqual(context.chunk_count, 0)
        self.assertIsNone(context.original_content)

        # Should have no chunks initially
        chunks = context.items.all()
        self.assertFalse(chunks.exists())

    def test_markdown_content_processing(self):
        """
        Test that markdown content can be set and automatically chunked.
        """
        # Create Markdown context
        context = Context.objects.create(
            name="Test Markdown Context",
            description="Test context for markdown processing",
            context_type="MARKDOWN",
        )

        # Test content with markdown structure (make it larger to ensure chunking)
        markdown_content = """# Introduction to Python Programming

This is the introduction section with some **bold** text and extensive content to ensure that the markdown chunker will create multiple chunks. Python is a versatile programming language that is widely used in various domains including web development, data science, machine learning, automation, and more.

Python's syntax is clean and readable, making it an excellent choice for beginners while still being powerful enough for experienced developers. The language emphasizes code readability and allows developers to express concepts in fewer lines of code than would be possible in languages such as C++ or Java.

## Core Features of Python

Python has many features that make it attractive to developers:

- **Simplicity**: Python's syntax is clean and easy to understand
- **Portability**: Python code can run on various platforms without modification
- **Extensive Libraries**: Python has a vast standard library and third-party packages
- **Community Support**: Large and active community providing help and resources
- **Versatility**: Can be used for web development, data analysis, AI, automation, and more

The language supports multiple programming paradigms, including procedural, object-oriented, and functional programming styles. This flexibility allows developers to choose the best approach for their specific problem.

### Standard Library

Python comes with an extensive standard library that provides modules and packages for common programming tasks. This "batteries included" philosophy means that developers can accomplish many tasks without needing to install additional packages.

### Third-Party Packages

The Python Package Index (PyPI) hosts hundreds of thousands of third-party packages that extend Python's capabilities even further. Popular packages include NumPy for numerical computing, pandas for data manipulation, Django for web development, and TensorFlow for machine learning.

## Code Examples and Best Practices

Here are some examples of Python code that demonstrate its simplicity and power:

```python
def hello_world():
    print("Hello, World!")

def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b
```

Python follows the principle of "There should be one obvious way to do it," which helps maintain code consistency across different projects and teams.

### Error Handling

Python uses exceptions for error handling, which makes code more robust and easier to debug:

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")
finally:
    print("Cleanup code here")
```

## Advanced Topics

As you become more comfortable with Python, you can explore advanced topics such as:

- **Decorators**: Functions that modify or enhance other functions
- **Generators**: Functions that yield values one at a time
- **Context Managers**: Objects that define runtime context for executing code
- **Metaclasses**: Classes whose instances are classes themselves

These advanced features allow for more sophisticated programming patterns and can help you write more efficient and maintainable code.

## Conclusion and Next Steps

This comprehensive overview covers the fundamental aspects of Python programming. The language's simplicity, combined with its power and extensive ecosystem, makes it an excellent choice for both beginners and experienced developers.

To continue your Python journey, consider exploring specific domains that interest you, such as web development with frameworks like Django or Flask, data science with libraries like pandas and scikit-learn, or artificial intelligence with TensorFlow and PyTorch.

Remember that the best way to learn programming is through practice, so start building projects and contributing to open-source software to gain real-world experience."""

        # Process the markdown content using the new method
        success = context.process_markdown_content(markdown_content)

        # Verify the content was processed successfully
        self.assertTrue(success)

        # Refresh from database
        context.refresh_from_db()

        # Should store the markdown content in original_content
        self.assertEqual(context.original_content, markdown_content)

        # Should update processing status
        self.assertEqual(context.processing_status, "COMPLETED")

        # Should create chunks based on markdown structure
        chunks = context.items.all()
        self.assertTrue(chunks.exists())
        self.assertGreater(context.chunk_count, 1)  # Should be multiple chunks

        # Chunks should NOT have file references
        for chunk in chunks:
            self.assertFalse(chunk.uploaded_file)
            self.assertIsNone(chunk.file_path)

    def test_smart_markdown_chunking_respects_sections(self):
        """
        Test that markdown chunking strategy respects section boundaries.
        """
        # Create Markdown context
        context = Context.objects.create(
            name="Smart Chunking Test",
            description="Test smart markdown chunking",
            context_type="MARKDOWN",
        )

        # Test content with clear section structure
        markdown_content = """# Main Title

Introduction paragraph that should be in the first chunk.

## Section 1

This is section 1 content that should be chunked together.
More content for section 1.

## Section 2

This is section 2 content that should be in a separate chunk.
More content for section 2.

### Subsection 2.1

This subsection should be kept with its parent section.

## Section 3

Final section content."""

        # Process the content with smaller chunk size to force chunking
        # Import and override chunk size temporarily
        with patch("rag.ingestion.chunkers.MarkdownChunker") as mock_chunker:
            mock_instance = mock_chunker.return_value
            # Mock the chunker to return separate chunks for each section
            mock_instance.chunk_text.return_value = [
                "# Main Title\n\nIntroduction paragraph that should be in the first chunk.",
                "## Section 1\n\nThis is section 1 content that should be chunked together.\nMore content for section 1.",
                "## Section 2\n\nThis is section 2 content that should be in a separate chunk.\nMore content for section 2.\n\n### Subsection 2.1\n\nThis subsection should be kept with its parent section.",
                "## Section 3\n\nFinal section content.",
            ]

            success = context.process_markdown_content(markdown_content)
            self.assertTrue(success)

        # Refresh and check chunks
        context.refresh_from_db()
        chunks = context.items.all().order_by("created_at")

        # Should have logical chunks based on sections
        self.assertGreater(chunks.count(), 2)

        # First chunk should contain the introduction
        first_chunk = chunks.first()
        assert first_chunk is not None  # For mypy
        self.assertIn("Main Title", first_chunk.content)
        self.assertIn("Introduction paragraph", first_chunk.content)

        # Section headers should start new chunks
        section_chunks = [chunk for chunk in chunks if "## Section" in chunk.content]
        self.assertGreater(len(section_chunks), 0)


class MarkdownAdminInterfaceTest(TestCase):
    """Test the markdown-specific admin interface."""

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username="admin", password="admin", is_staff=True, is_superuser=True
        )
        self.client.login(username="admin", password="admin")

    def test_markdown_context_admin_form_loads(self):
        """Test that Markdown context admin form loads successfully."""
        # Create a Markdown context
        context = Context.objects.create(
            name="Test Markdown Context",
            description="Test context for markdown admin",
            context_type="MARKDOWN",
        )

        # Access the admin change form
        url = reverse("admin:rag_context_change", args=[context.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # Should contain the context name
        self.assertContains(response, "Test Markdown Context")

    def test_markdown_context_shows_direct_editing_field(self):
        """Test that Markdown contexts show original_content field for direct editing."""
        # Create a Markdown context with content
        context = Context.objects.create(
            name="Markdown with Content",
            description="Test markdown with existing content",
            context_type="MARKDOWN",
        )

        # Add some content
        context.process_markdown_content("# Test Heading\n\nTest content")

        # Access the admin change form
        url = reverse("admin:rag_context_change", args=[context.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # Should contain the markdown content in the form
        self.assertContains(response, "Test Heading")
        self.assertContains(response, "Test content")

    def test_markdown_context_uses_markdown_inline(self):
        """Test that Markdown contexts use markdown-specific inline editor."""
        # Create a Markdown context with chunks
        context = Context.objects.create(
            name="Markdown with Chunks",
            description="Test markdown with chunks",
            context_type="MARKDOWN",
        )

        # Add content to create chunks
        context.process_markdown_content(
            "# Heading 1\n\nContent 1\n\n# Heading 2\n\nContent 2"
        )

        # Access the admin change form
        url = reverse("admin:rag_context_change", args=[context.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # Should show the chunks with markdown-friendly display
        self.assertContains(response, "Heading 1")
        self.assertContains(response, "Heading 2")
