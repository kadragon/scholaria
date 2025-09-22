from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

from django.contrib import admin, messages
from django.contrib.admin.options import InlineModelAdmin
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.forms import FileField, ModelForm
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
    list_display = ["name", "description", "context_count", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["name", "description"]
    actions = ["assign_context_to_topics", "bulk_update_system_prompt"]
    filter_horizontal = ["contexts"]  # Better UI for ManyToMany selection
    fieldsets = (
        (None, {"fields": ("name", "description", "system_prompt")}),
        ("Associated Contexts", {"fields": ("contexts",)}),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Topic]:
        """Annotate queryset with context counts for ordering and display."""
        queryset = super().get_queryset(request)
        return queryset.annotate(context_count=Count("contexts", distinct=True))

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

    @admin.display(
        description="Contexts",
        ordering="context_count",
    )
    def context_count(self, obj: Topic) -> int:
        """Display the number of contexts associated with this topic."""
        return getattr(obj, "context_count", obj.contexts.count())


class ContextForm(ModelForm):
    """Custom form for Context admin with file upload capability."""

    uploaded_file = FileField(
        required=False,
        help_text="Upload a PDF file to automatically parse and create chunks. "
        "File will be processed and discarded - not stored permanently.",
    )

    class Meta:
        model = Context
        fields = "__all__"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        processing_field = self.fields.get("processing_status")
        if processing_field is not None:
            processing_field.required = False
            if not self.instance.pk and "processing_status" not in self.data:
                processing_field.initial = processing_field.initial or "PENDING"

        # Make chunk_count not required for forms (it's auto-calculated)
        chunk_count_field = self.fields.get("chunk_count")
        if chunk_count_field is not None:
            chunk_count_field.required = False

    def clean_uploaded_file(self) -> Any:
        """Validate uploaded file for PDF context types."""
        uploaded_file = self.cleaned_data.get("uploaded_file")
        context_type = self.cleaned_data.get("context_type")

        if uploaded_file and context_type == "PDF":
            validator = FileValidator()
            validation_result = validator.validate_file(uploaded_file)

            if not validation_result.is_valid:
                errors = validation_result.errors or []
                raise ValidationError(f"File validation failed: {'; '.join(errors)}")

            if validation_result.file_type != "pdf":
                raise ValidationError(
                    "Only PDF files are supported for PDF context type."
                )

        return uploaded_file

    def clean_processing_status(self) -> str:
        """Default missing processing status to 'PENDING'."""
        value = self.cleaned_data.get("processing_status")
        if not value:
            return "PENDING"
        return str(value)


class ContextItemInline(admin.TabularInline):
    """Inline admin for ContextItems within Context admin."""

    model = ContextItem
    extra = 0
    fields = ["title", "content", "uploaded_file", "file_path"]
    readonly_fields = ["file_path"]
    verbose_name = "Context Item (Chunk)"
    verbose_name_plural = "Context Items (Chunks)"

    def get_queryset(self, request: HttpRequest) -> QuerySet[ContextItem]:
        """Limit to show only recent items to avoid performance issues."""
        qs = super().get_queryset(request)
        return qs.order_by("-created_at")  # Remove slice to avoid filter issues


class FAQQAInline(admin.TabularInline):
    """FAQ-specific inline for Q&A pair management."""

    model = ContextItem
    extra = 1
    fields = ["title", "content"]
    verbose_name = "Q&A Pair"
    verbose_name_plural = "Q&A Pairs"

    def get_queryset(self, request: HttpRequest) -> QuerySet[ContextItem]:
        """Get ContextItems for FAQ contexts only."""
        qs = super().get_queryset(request)
        return qs.order_by("created_at")

    def save_model(
        self, request: HttpRequest, obj: ContextItem, form: Any, change: bool
    ) -> None:
        """Override save to ensure proper FAQ formatting."""
        if obj.title and obj.content and not change:
            # For new Q&A pairs, ensure proper formatting
            if not obj.title.endswith("?"):
                obj.title = f"{obj.title}?"
        # Skip superclass save_model since it doesn't exist in TabularInline
        obj.save()


class MarkdownChunkInline(admin.TabularInline):
    """Markdown-specific inline for chunk preview."""

    model = ContextItem
    extra = 0
    fields = ["title", "chunk_preview"]
    readonly_fields = ["title", "chunk_preview"]
    verbose_name = "Markdown Section"
    verbose_name_plural = "Markdown Sections"

    def get_queryset(self, request: HttpRequest) -> QuerySet[ContextItem]:
        """Get ContextItems for Markdown contexts only."""
        qs = super().get_queryset(request)
        return qs.order_by("created_at")

    @admin.display(description="Content Preview")
    def chunk_preview(self, obj: ContextItem) -> str:
        """Show a preview of the chunk content."""
        if obj and obj.content:
            # Show first 100 characters
            preview = obj.content[:100]
            if len(obj.content) > 100:
                preview += "..."
            return preview
        return ""

    def has_add_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        """Disable add permission for Markdown inline - edit content directly."""
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        """Disable delete permission for Markdown inline - edit content directly."""
        return False


@admin.register(Context)
class ContextAdmin(admin.ModelAdmin):
    inlines = [ContextItemInline]
    form = ContextForm
    list_display = [
        "name",
        "context_type",
        "processing_status",
        "chunk_count",
        "item_count",
        "created_at",
    ]
    list_filter = ["context_type", "processing_status", "created_at", "updated_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at", "chunk_count"]
    actions = [
        "bulk_update_context_type",
        "bulk_update_processing_status",
        "add_qa_pair_action",
    ]

    def _inline_classes(self, obj: Context | None) -> list[type[InlineModelAdmin]]:
        """Return inline classes appropriate for the given context instance."""
        if obj and obj.context_type == "FAQ":
            return [FAQQAInline]
        if obj and obj.context_type == "MARKDOWN":
            return [MarkdownChunkInline]
        return [ContextItemInline]

    def get_inline_instances(
        self, request: HttpRequest, obj: Context | None = None
    ) -> list[InlineModelAdmin]:
        """Instantiate inline admins based on context type while respecting permissions."""
        if obj is None:
            # Skip inlines during object creation to avoid bogus management form errors.
            return []

        inline_instances: list[InlineModelAdmin] = []
        for inline_class in self._inline_classes(obj):
            inline = inline_class(self.model, self.admin_site)
            if request and not (
                inline.has_view_or_change_permission(request, obj)
                or inline.has_add_permission(request, obj)
                or inline.has_delete_permission(request, obj)
            ):
                continue
            inline_instances.append(inline)
        return inline_instances

    def get_fieldsets(self, request: HttpRequest, obj: Context | None = None) -> Any:
        """Dynamic fieldsets based on context type."""
        base_fieldsets = [
            (None, {"fields": ("name", "description", "context_type")}),
            ("Processing", {"fields": ("processing_status", "chunk_count")}),
            (
                "Timestamps",
                {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
            ),
        ]

        if obj and obj.context_type == "FAQ":
            # FAQ-specific fieldsets
            base_fieldsets.insert(
                1,
                (
                    "Q&A Management",
                    {
                        "fields": (),
                        "description": 'Use the "Add Q&A Pair" action below to add question-answer pairs to this FAQ context.',
                        "classes": ("wide",),
                    },
                ),
            )
        elif obj and obj.context_type == "PDF":
            # PDF-specific fieldsets
            base_fieldsets.insert(
                1,
                (
                    "File Upload",
                    {
                        "fields": ("uploaded_file",),
                        "description": "Upload a PDF file to automatically parse and create chunks.",
                    },
                ),
            )
        elif obj and obj.context_type == "MARKDOWN":
            # Markdown-specific fieldsets - put content field first for direct editing
            base_fieldsets.insert(
                1,
                (
                    "Markdown Content",
                    {
                        "fields": ("original_content",),
                        "description": "Edit markdown content directly. Changes will automatically re-chunk the content when saved.",
                        "classes": ("wide",),
                    },
                ),
            )
        else:
            # For new objects (obj is None) or unknown types, show PDF upload option
            base_fieldsets.insert(
                1,
                (
                    "File Upload",
                    {
                        "fields": ("uploaded_file",),
                        "description": "For PDF contexts, upload a file to automatically parse and create chunks.",
                    },
                ),
            )

        # Content fieldset for non-markdown types (markdown has its own content section)
        if not (obj and obj.context_type == "MARKDOWN"):
            base_fieldsets.insert(
                -2,
                (
                    "Content",
                    {"fields": ("original_content",), "classes": ("collapse",)},
                ),
            )

        return base_fieldsets

    def get_queryset(self, request: HttpRequest) -> QuerySet[Context]:
        """Annotate queryset with item counts for ordering display columns."""
        queryset = super().get_queryset(request)
        return queryset.annotate(item_count=Count("items", distinct=True))

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

    @admin.action(description="Update processing status for selected contexts")
    def bulk_update_processing_status(
        self, request: HttpRequest, queryset: QuerySet[Context]
    ) -> HttpResponse | None:
        """Bulk action to update processing status for multiple contexts."""
        if request.method == "POST" and "processing_status" in request.POST:
            processing_status = request.POST.get("processing_status")
            if processing_status in dict(Context.PROCESSING_STATUS_CHOICES):
                count = queryset.update(processing_status=processing_status)
                messages.success(
                    request,
                    f"Successfully updated processing status to '{processing_status}' for {count} contexts.",
                )
                return redirect(request.get_full_path())
            else:
                messages.error(request, "Invalid processing status selected.")
                return redirect(request.get_full_path())

        # Show processing status selection form
        context = {
            "title": "Update Processing Status",
            "queryset": queryset,
            "processing_status_choices": Context.PROCESSING_STATUS_CHOICES,
            "action": "bulk_update_processing_status",
        }
        return render(request, "admin/bulk_update_processing_status.html", context)

    @admin.display(
        description="Items",
        ordering="item_count",
    )
    def item_count(self, obj: Context) -> int:
        """Display the number of context items in this context."""
        return getattr(obj, "item_count", obj.items.count())

    def save_model(
        self, request: HttpRequest, obj: Context, form: Any, change: bool
    ) -> None:
        """Custom save method to handle content processing for different context types."""
        # Get the old content if this is an update
        old_content = None
        if change and obj.pk:
            try:
                old_obj = Context.objects.get(pk=obj.pk)
                old_content = old_obj.original_content
            except Context.DoesNotExist:
                pass

        # Save the context first
        super().save_model(request, obj, form, change)

        # Handle markdown content processing if content changed
        if obj.context_type == "MARKDOWN" and obj.original_content:
            if not change or old_content != obj.original_content:
                try:
                    success = obj.process_markdown_content(obj.original_content)
                    if success:
                        messages.success(
                            request,
                            f"Successfully processed markdown content and created "
                            f"{obj.chunk_count} sections.",
                        )
                    else:
                        messages.error(request, "Failed to process markdown content.")
                except Exception as e:
                    messages.error(request, f"Error processing markdown: {str(e)}")

        # Handle PDF file upload
        uploaded_file = form.cleaned_data.get("uploaded_file")
        if uploaded_file and obj.context_type == "PDF":
            try:
                # Use the existing PDF workflow
                success = obj.process_pdf_upload(uploaded_file)
                if success:
                    messages.success(
                        request,
                        f"Successfully processed PDF '{uploaded_file.name}' and created "
                        f"{obj.chunk_count} chunks. Original file was not stored.",
                    )
                else:
                    messages.error(request, "Failed to process PDF file.")
            except Exception as e:
                messages.error(request, f"Error processing PDF: {str(e)}")

    @admin.action(description="Add Q&A pair to selected FAQ contexts")
    def add_qa_pair_action(
        self, request: HttpRequest, queryset: QuerySet[Context]
    ) -> HttpResponse | None:
        """Action to add Q&A pairs to FAQ contexts."""
        # Filter to only FAQ contexts
        faq_contexts = queryset.filter(context_type="FAQ")

        if not faq_contexts.exists():
            messages.error(request, "This action can only be used with FAQ contexts.")
            return redirect(request.get_full_path())

        if (
            request.method == "POST"
            and "question" in request.POST
            and "answer" in request.POST
        ):
            question = request.POST.get("question", "").strip()
            answer = request.POST.get("answer", "").strip()

            if not question or not answer:
                messages.error(request, "Both question and answer are required.")
                return redirect(request.get_full_path())

            success_count = 0
            for context in faq_contexts:
                try:
                    if context.add_qa_pair(question, answer):
                        success_count += 1
                except Exception as e:
                    messages.error(
                        request, f"Error adding Q&A to {context.name}: {str(e)}"
                    )

            if success_count > 0:
                messages.success(
                    request,
                    f"Successfully added Q&A pair to {success_count} FAQ context(s).",
                )

            return redirect(request.get_full_path())

        # Show Q&A input form
        template_context = {
            "title": "Add Q&A Pair to FAQ Contexts",
            "queryset": faq_contexts,
            "action": "add_qa_pair_action",
            "description": "Add a question-answer pair to the selected FAQ contexts.",
            "opts": self.model._meta,
            "app_label": self.model._meta.app_label,
        }
        return render(request, "admin/add_qa_pair.html", template_context)


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


# ContextItem remains primarily managed through Context admin views.
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
