from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import Context, ContextItem, Topic
from .storage import MinIOStorage
from .validators import FileValidator

if TYPE_CHECKING:
    from django.core.files.uploadedfile import UploadedFile
    from django.http import HttpRequest


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["name", "description"]
    fieldsets = (
        (None, {"fields": ("name", "description", "system_prompt")}),
        ("Relationships", {"fields": ("contexts",)}),
    )


@admin.register(Context)
class ContextAdmin(admin.ModelAdmin):
    list_display = ["name", "context_type", "description", "created_at"]
    list_filter = ["context_type", "created_at", "updated_at"]
    search_fields = ["name", "description"]


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

    @admin.display(
        description="Has File",
        boolean=True,
    )
    def has_uploaded_file(self, obj: ContextItem) -> bool:
        """Display whether the item has an uploaded file."""
        return bool(obj.uploaded_file)

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
                # For now, just set a placeholder - this could be enhanced with
                # automatic content extraction based on file type
                obj.content = f"Content from uploaded file: {obj.uploaded_file.name}"

        super().save_model(request, obj, form, change)
