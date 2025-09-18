from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.db import models

if TYPE_CHECKING:
    from typing import Any


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

    name = models.CharField(max_length=200)
    description = models.TextField()
    context_type = models.CharField(max_length=20, choices=CONTEXT_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self) -> None:
        if not self.name:
            raise ValidationError({"name": "This field is required."})
        if not self.description:
            raise ValidationError({"description": "This field is required."})
        if not self.context_type:
            raise ValidationError({"context_type": "This field is required."})

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name"]

    # Type hints for reverse relationships
    if TYPE_CHECKING:
        topics: Any  # ManyToMany reverse manager


class ContextItem(models.Model):
    title = models.CharField(max_length=300)
    content = models.TextField()
    context = models.ForeignKey(Context, on_delete=models.CASCADE, related_name="items")
    file_path = models.CharField(max_length=500, blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self) -> None:
        if not self.title:
            raise ValidationError({"title": "This field is required."})
        if not self.content:
            raise ValidationError({"content": "This field is required."})
        if not self.context_id:
            raise ValidationError({"context": "This field is required."})

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["created_at"]
