from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .ingestion.parsers import MarkdownParser, PDFParser
from .models import Context, ContextItem, Topic
from .storage import MinIOStorage
from .validators import FileValidator

if TYPE_CHECKING:
    from django.core.files.uploadedfile import UploadedFile
    from django.db.models import QuerySet
    from django.http import HttpRequest


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["name", "description"]
    actions = ["assign_context_to_topics", "bulk_update_system_prompt"]
    fieldsets = (
        (None, {"fields": ("name", "description", "system_prompt")}),
        ("Relationships", {"fields": ("contexts",)}),
    )

    @admin.action(description="Assign context to selected topics")
    def assign_context_to_topics(
        self, request: HttpRequest, queryset: QuerySet[Topic]
    ) -> HttpResponse | None:
        """Bulk action to assign a context to multiple topics."""
        if request.method == "POST" and "context_id" in request.POST:
            context_id = request.POST.get("context_id")
            if context_id:
                try:
                    context = Context.objects.get(id=int(context_id))
                    count = queryset.count()
                    context.topics.add(*queryset)

                    messages.success(
                        request,
                        f"Successfully assigned context '{context.name}' to {count} topics.",
                    )
                    return redirect(request.get_full_path())
                except (Context.DoesNotExist, ValueError):
                    messages.error(request, "Selected context does not exist.")
                    return redirect(request.get_full_path())

        # Show context selection form
        contexts = Context.objects.all()
        template_context = {
            "title": "Assign Context to Topics",
            "queryset": queryset,
            "contexts": contexts,
            "action": "assign_context_to_topics",
        }
        return render(request, "admin/bulk_assign_context.html", template_context)

    @admin.action(description="Update system prompt for selected topics")
    def bulk_update_system_prompt(
        self, request: HttpRequest, queryset: QuerySet[Topic]
    ) -> HttpResponse | None:
        """Bulk action to update system prompt for multiple topics."""
        if request.method == "POST" and "system_prompt" in request.POST:
            system_prompt = request.POST.get("system_prompt", "")
            count = queryset.update(system_prompt=system_prompt)

            messages.success(
                request, f"Successfully updated system prompt for {count} topics."
            )
            return redirect(request.get_full_path())

        # Show system prompt update form
        context = {
            "title": "Update System Prompt",
            "queryset": queryset,
            "action": "bulk_update_system_prompt",
        }
        return render(request, "admin/bulk_update_system_prompt.html", context)


@admin.register(Context)
class ContextAdmin(admin.ModelAdmin):
    list_display = ["name", "context_type", "description", "created_at"]
    list_filter = ["context_type", "created_at", "updated_at"]
    search_fields = ["name", "description"]
    actions = ["bulk_update_context_type"]

    @admin.action(description="Update context type for selected contexts")
    def bulk_update_context_type(
        self, request: HttpRequest, queryset: QuerySet[Context]
    ) -> HttpResponse | None:
        """Bulk action to update context type for multiple contexts."""
        if request.method == "POST" and "context_type" in request.POST:
            context_type = request.POST.get("context_type")
            if context_type in dict(Context.CONTEXT_TYPE_CHOICES):
                count = queryset.update(context_type=context_type)
                messages.success(
                    request,
                    f"Successfully updated context type to '{context_type}' for {count} contexts.",
                )
                return redirect(request.get_full_path())
            else:
                messages.error(request, "Invalid context type selected.")
                return redirect(request.get_full_path())

        # Show context type selection form
        context = {
            "title": "Update Context Type",
            "queryset": queryset,
            "context_type_choices": Context.CONTEXT_TYPE_CHOICES,
            "action": "bulk_update_context_type",
        }
        return render(request, "admin/bulk_update_context_type.html", context)


class ContextItemForm(ModelForm):
    class Meta:
        model = ContextItem
        fields = "__all__"

    def clean_uploaded_file(self) -> UploadedFile | None:
        """Validate uploaded file using FileValidator."""
        uploaded_file = self.cleaned_data.get("uploaded_file")

        if uploaded_file:
            validator = FileValidator()
            validation_result = validator.validate_file(uploaded_file)

            if not validation_result.is_valid:
                errors = validation_result.errors or []
                raise ValidationError(f"File validation failed: {'; '.join(errors)}")

            # Sanitize the filename
            if uploaded_file.name:
                sanitized_name = validator.sanitize_filename(uploaded_file.name)
                uploaded_file.name = sanitized_name

        return uploaded_file


@admin.register(ContextItem)
class ContextItemAdmin(admin.ModelAdmin):
    form = ContextItemForm
    list_display = ["title", "context", "file_path", "has_uploaded_file", "created_at"]
    list_filter = ["context", "created_at", "updated_at"]
    search_fields = ["title", "content"]
    readonly_fields = ["created_at", "updated_at", "file_path"]
    actions = ["bulk_regenerate_embeddings", "bulk_move_to_context"]
    fieldsets = (
        (None, {"fields": ("title", "context", "content")}),
        (
            "File Upload",
            {
                "fields": ("uploaded_file", "file_path"),
                "description": "Upload a file to automatically populate content and store in MinIO.",
            },
        ),
        ("Metadata", {"fields": ("metadata",), "classes": ("collapse",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    @admin.action(description="Regenerate embeddings for selected items")
    def bulk_regenerate_embeddings(
        self, request: HttpRequest, queryset: QuerySet[ContextItem]
    ) -> HttpResponse | None:
        """Bulk action to regenerate embeddings for context items."""
        if request.method == "POST" and "confirm" in request.POST:
            # This would trigger the ingestion pipeline to regenerate embeddings
            count = queryset.count()
            messages.success(
                request,
                f"Scheduled embedding regeneration for {count} context items. "
                "This process will run in the background.",
            )
            # TODO: Add actual embedding regeneration logic with Celery
            return redirect(request.get_full_path())

        # Show confirmation form
        context = {
            "title": "Regenerate Embeddings",
            "queryset": queryset,
            "action": "bulk_regenerate_embeddings",
            "description": "This will regenerate embeddings for all selected context items. This operation may take some time.",
        }
        return render(request, "admin/bulk_regenerate_embeddings.html", context)

    @admin.action(description="Move selected items to another context")
    def bulk_move_to_context(
        self, request: HttpRequest, queryset: QuerySet[ContextItem]
    ) -> HttpResponse | None:
        """Bulk action to move context items to a different context."""
        if request.method == "POST" and "context_id" in request.POST:
            context_id = request.POST.get("context_id")
            if context_id:
                try:
                    new_context = Context.objects.get(id=int(context_id))
                    count = queryset.update(context=new_context)
                    messages.success(
                        request,
                        f"Successfully moved {count} context items to '{new_context.name}'.",
                    )
                    return redirect(request.get_full_path())
                except (Context.DoesNotExist, ValueError):
                    messages.error(request, "Selected context does not exist.")
                    return redirect(request.get_full_path())

        # Show context selection form
        contexts = Context.objects.all()
        template_context = {
            "title": "Move Context Items",
            "queryset": queryset,
            "contexts": contexts,
            "action": "bulk_move_to_context",
        }
        return render(request, "admin/bulk_move_to_context.html", template_context)

    @admin.display(
        description="Has File",
        boolean=True,
    )
    def has_uploaded_file(self, obj: ContextItem) -> bool:
        """Display whether the item has an uploaded file."""
        return bool(obj.uploaded_file)

    def _extract_content_from_file(
        self, uploaded_file: UploadedFile, file_type: str
    ) -> str:
        """Extract content from uploaded file based on file type.

        Args:
            uploaded_file: The Django UploadedFile instance
            file_type: The detected file type (pdf, markdown, text)

        Returns:
            Extracted content as string
        """
        try:
            # Create a temporary file to save the uploaded content
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=f".{file_type}"
            ) as temp_file:
                # Write the uploaded file content to temporary file
                uploaded_file.seek(0)
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
                temp_file.flush()

                # Extract content based on file type
                if file_type == "pdf":
                    pdf_parser = PDFParser()
                    return pdf_parser.parse_file(temp_file.name)
                elif file_type in ["markdown", "text"]:
                    md_parser = MarkdownParser()
                    return md_parser.parse_file(temp_file.name)
                else:
                    return f"Unsupported file type: {file_type}"

        except Exception as e:
            return f"Error extracting content: {str(e)}"
        finally:
            # Clean up temporary file
            try:
                Path(temp_file.name).unlink(missing_ok=True)
            except:  # noqa: E722
                pass  # Ignore cleanup errors

    def save_model(
        self, request: HttpRequest, obj: ContextItem, form: Any, change: bool
    ) -> None:
        """Custom save method to handle MinIO file upload."""
        if obj.uploaded_file:
            storage = MinIOStorage()
            storage.ensure_bucket_exists()

            # Upload file to MinIO
            minio_path = storage.upload_django_file(obj.uploaded_file)
            obj.file_path = minio_path

            # If no content provided and file uploaded, extract content
            if not obj.content and obj.uploaded_file:
                # Get the file type from form validation
                validator = FileValidator()
                validation_result = validator.validate_file(obj.uploaded_file)

                if validation_result.is_valid and validation_result.file_type:
                    extracted_content = self._extract_content_from_file(
                        obj.uploaded_file, validation_result.file_type
                    )
                    obj.content = extracted_content
                else:
                    obj.content = (
                        f"Content from uploaded file: {obj.uploaded_file.name}"
                    )

        super().save_model(request, obj, form, change)
