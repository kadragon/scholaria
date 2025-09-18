from django.core.exceptions import ValidationError
from django.db import models


class Topic(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    system_prompt = models.TextField(blank=True, null=True)
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
