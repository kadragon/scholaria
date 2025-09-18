from django.contrib import admin

from .models import Context, ContextItem, Topic


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


@admin.register(ContextItem)
class ContextItemAdmin(admin.ModelAdmin):
    list_display = ["title", "context", "file_path", "created_at"]
    list_filter = ["context", "created_at", "updated_at"]
    search_fields = ["title", "content"]
    readonly_fields = ["created_at", "updated_at"]
