from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver


class Topic(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    system_prompt = models.TextField(blank=True, null=True)
    contexts: models.ManyToManyField[Context, Topic] = models.ManyToManyField(
        "Context", related_name="topics", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self) -> None:
        if not self.name:
            raise ValidationError({"name": "This field is required."})
        if not self.description:
            raise ValidationError({"description": "This field is required."})

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name"]


class Context(models.Model):
    CONTEXT_TYPE_CHOICES = [
        ("PDF", "PDF"),
        ("FAQ", "FAQ"),
        ("MARKDOWN", "Markdown"),
    ]

    PROCESSING_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    context_type = models.CharField(max_length=20, choices=CONTEXT_TYPE_CHOICES)
    original_content = models.TextField(
        blank=True, null=True, help_text="Full document content before chunking"
    )
    chunk_count = models.PositiveIntegerField(
        default=0, help_text="Number of chunks created from this context"
    )
    processing_status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS_CHOICES,
        default="PENDING",
        help_text="Current processing status of the context",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self) -> None:
        if not self.name:
            raise ValidationError({"name": "This field is required."})
        if not self.description:
            raise ValidationError({"description": "This field is required."})
        if not self.context_type:
            raise ValidationError({"context_type": "This field is required."})
        if self.processing_status and self.processing_status not in dict(
            self.PROCESSING_STATUS_CHOICES
        ):
            raise ValidationError({"processing_status": "Invalid processing status."})

    def update_chunk_count(self) -> None:
        """Recalculate and persist the number of associated context items."""
        if not self.pk:
            return
        new_count = self.items.count()
        Context.objects.filter(pk=self.pk).update(chunk_count=new_count)
        self.chunk_count = new_count

    def process_pdf_upload(self, uploaded_file: Any) -> bool:
        """
        Process PDF upload with parse → chunk → discard workflow.

        Args:
            uploaded_file: Django UploadedFile instance

        Returns:
            True if successful, False otherwise
        """
        try:
            # Import here to avoid circular imports
            from .ingestion.chunkers import TextChunker
            from .ingestion.parsers import PDFParser

            self.processing_status = "PROCESSING"
            self.save(update_fields=["processing_status"])

            # Create temporary file for parsing
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                # Write uploaded file content to temporary file
                uploaded_file.seek(0)
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
                temp_file.flush()

                # Parse PDF content
                parser = PDFParser()
                parsed_content = parser.parse_file(temp_file.name)

                # Store original content in Context
                self.original_content = parsed_content

                # Create chunks from parsed content
                chunker = TextChunker(chunk_size=1000, overlap=200)
                chunks = chunker.chunk_text(parsed_content)

                # Create ContextItem instances for each chunk
                for i, chunk_content in enumerate(chunks):
                    ContextItem.objects.create(
                        title=f"{self.name} - Chunk {i+1}",
                        content=chunk_content,
                        context=self,
                        # Important: No uploaded_file or file_path - we discard the file
                    )

                # Update processing status and chunk count
                self.processing_status = "COMPLETED"
                self.update_chunk_count()
                self.save(update_fields=["original_content", "processing_status"])

                return True

        except Exception as e:
            self.processing_status = "FAILED"
            self.save(update_fields=["processing_status"])
            raise e
        finally:
            # Clean up temporary file
            try:
                Path(temp_file.name).unlink(missing_ok=True)
            except:  # noqa: E722
                pass

    def add_qa_pair(self, question: str, answer: str) -> bool:
        """
        Add a Q&A pair to an FAQ context.
        Each Q&A pair becomes a separate chunk (1 Q&A pair = 1 chunk).

        Args:
            question: The question text
            answer: The answer text

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.context_type != "FAQ":
                raise ValueError("add_qa_pair can only be used with FAQ contexts")

            # Format the Q&A pair content
            qa_content = f"Q: {question.strip()}\nA: {answer.strip()}"

            # Get the next Q&A number for the title
            current_count = self.items.count()
            qa_number = current_count + 1

            # Create a ContextItem for this Q&A pair
            ContextItem.objects.create(
                title=f"{self.name} - Q&A {qa_number}",
                content=qa_content,
                context=self,
                # No uploaded_file or file_path for FAQ pairs
            )

            # Update the original_content to include all Q&A pairs
            all_qa_pairs = []
            for item in self.items.all().order_by("created_at"):
                all_qa_pairs.append(item.content)

            self.original_content = "\n\n".join(all_qa_pairs)

            # Update processing status and chunk count
            if self.processing_status == "PENDING":
                self.processing_status = "COMPLETED"

            self.update_chunk_count()
            self.save(update_fields=["original_content", "processing_status"])

            return True

        except Exception:
            return False

    def process_markdown_content(self, markdown_content: str) -> bool:
        """
        Process markdown content with smart chunking strategy.

        Args:
            markdown_content: The markdown content as a string

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.context_type != "MARKDOWN":
                raise ValueError(
                    "process_markdown_content can only be used with MARKDOWN contexts"
                )

            # Import here to avoid circular imports
            from .ingestion.chunkers import MarkdownChunker

            self.processing_status = "PROCESSING"
            self.save(update_fields=["processing_status"])

            # Store the original markdown content
            self.original_content = markdown_content.strip()

            # Create chunks using smart markdown chunking
            chunker = MarkdownChunker(chunk_size=1200, overlap=200)
            chunks = chunker.chunk_text(markdown_content)

            # Clear existing chunks for this context
            self.items.all().delete()

            # Create ContextItem instances for each chunk
            for i, chunk_content in enumerate(chunks):
                # Create meaningful titles based on content
                title = self._generate_chunk_title(chunk_content, i + 1)

                ContextItem.objects.create(
                    title=title,
                    content=chunk_content,
                    context=self,
                    # No uploaded_file or file_path - content is directly edited
                )

            # Update processing status and chunk count
            self.processing_status = "COMPLETED"
            self.update_chunk_count()
            self.save(update_fields=["original_content", "processing_status"])

            return True

        except Exception:
            self.processing_status = "FAILED"
            self.save(update_fields=["processing_status"])
            return False

    def _generate_chunk_title(self, chunk_content: str, chunk_number: int) -> str:
        """Generate a meaningful title for a markdown chunk."""
        # Try to extract the first heading from the chunk
        lines = chunk_content.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                # Extract heading text (remove # symbols and clean up)
                heading = line.lstrip("#").strip()
                if heading:
                    return f"{self.name} - {heading}"

        # If no heading found, use generic chunk title
        return f"{self.name} - Section {chunk_number}"

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name"]

    # Type hints for reverse relationships
    if TYPE_CHECKING:
        topics: Any  # ManyToMany reverse manager


class ContextItem(models.Model):
    title = models.CharField(max_length=300)
    content = models.TextField(blank=True)
    context = models.ForeignKey(Context, on_delete=models.CASCADE, related_name="items")
    file_path = models.CharField(max_length=500, blank=True, null=True)
    uploaded_file = models.FileField(upload_to="uploads/", blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self) -> None:
        if not self.title:
            raise ValidationError({"title": "This field is required."})
        if not self.content and not self.uploaded_file:
            raise ValidationError(
                {"content": "Either content or uploaded file is required."}
            )
        if not self.context_id:
            raise ValidationError({"context": "This field is required."})

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["created_at"]


def _refresh_context_chunk_count(instance: ContextItem) -> None:
    """Helper to keep Context.chunk_count in sync with related items."""
    if instance.context_id:
        instance.context.update_chunk_count()


@receiver(post_save, sender=ContextItem)
def context_item_post_save(
    sender: type[ContextItem], instance: ContextItem, created: bool, **kwargs: Any
) -> None:
    """Update chunk count and generate embeddings when a context item is created or updated."""
    _refresh_context_chunk_count(instance)

    # Generate and store embeddings for new ContextItems asynchronously
    if created and instance.content:
        try:
            from rag.tasks import generate_context_item_embedding

            # Queue embedding generation as async task
            generate_context_item_embedding.delay(instance.id)
        except Exception as e:
            # Log the error but don't fail the save operation
            import logging

            logger = logging.getLogger(__name__)
            logger.error(
                f"Failed to queue embedding generation task for ContextItem {instance.id}: {e}"
            )


@receiver(post_delete, sender=ContextItem)
def context_item_post_delete(
    sender: type[ContextItem], instance: ContextItem, **kwargs: Any
) -> None:
    """Update chunk count when a context item is removed."""
    _refresh_context_chunk_count(instance)


class QuestionHistory(models.Model):
    """Model to store question and answer history for users."""

    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name="question_histories"
    )
    question = models.TextField(help_text="The question asked by the user")
    answer = models.TextField(help_text="The answer provided by the system")
    session_id = models.CharField(
        max_length=255, help_text="Session identifier to group related questions"
    )
    is_favorited = models.BooleanField(
        default=False, help_text="Whether this question is marked as favorite"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self) -> None:
        if not self.topic_id:
            raise ValidationError({"topic": "This field is required."})
        if not self.question:
            raise ValidationError({"question": "This field is required."})
        if not self.answer:
            raise ValidationError({"answer": "This field is required."})
        if not self.session_id:
            raise ValidationError({"session_id": "This field is required."})

    def __str__(self) -> str:
        return f"{self.question} ({self.topic.name})"

    class Meta:
        ordering = ["-created_at"]  # Newest first
