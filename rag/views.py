from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.serializers import (
    CharField,
    IntegerField,
    ModelSerializer,
    Serializer,
)
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView

from .models import Topic
from .retrieval.rag import RAGService

if TYPE_CHECKING:
    from django.db.models.query import QuerySet
    from django.http import HttpRequest, HttpResponse
    from rest_framework.request import Request


logger = logging.getLogger(__name__)


class TopicSerializer(ModelSerializer[Topic]):
    """Serializer for Topic model."""

    class Meta:
        model = Topic
        fields = [
            "id",
            "name",
            "description",
            "system_prompt",
            "created_at",
            "updated_at",
        ]


class TopicListView(generics.ListAPIView[Topic]):
    """API endpoint for retrieving all topics."""

    serializer_class = TopicSerializer
    pagination_class = None  # Disable pagination for simple topic list

    def get_queryset(self) -> QuerySet[Topic]:
        """Return all topics."""
        return Topic.objects.all()


class TopicDetailView(generics.RetrieveAPIView[Topic]):
    """API endpoint for retrieving a single topic by ID."""

    serializer_class = TopicSerializer

    def get_queryset(self) -> QuerySet[Topic]:
        """Return all topics."""
        return Topic.objects.all()


class QuestionSerializer(Serializer[dict[str, str | int]]):
    """Serializer for question input."""

    topic_id = IntegerField(min_value=1)
    question = CharField(max_length=5000)  # Limit question length

    def validate_question(self, value: str) -> str:
        """Validate that question is not empty and within reasonable limits."""
        if not value.strip():
            raise serializers.ValidationError("Question cannot be empty.")
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Question must be at least 3 characters long."
            )
        if len(value.strip()) > 5000:
            raise serializers.ValidationError(
                "Question is too long. Maximum 5000 characters allowed."
            )
        return value.strip()

    def validate_topic_id(self, value: int | None) -> int:
        """Validate that topic exists and is positive."""
        if value is None:
            raise serializers.ValidationError("Topic ID is required.")
        if value <= 0:
            raise serializers.ValidationError("Topic ID must be a positive integer.")
        try:
            Topic.objects.get(id=value)
        except Topic.DoesNotExist:
            raise serializers.ValidationError("Topic not found.") from None
        return value


class RAGQuestionThrottle(UserRateThrottle):
    """Custom throttle for RAG question endpoint."""

    scope = "rag_questions"


class AskQuestionView(APIView):
    """API endpoint for asking questions and getting RAG-based answers."""

    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle, RAGQuestionThrottle]

    def post(self, request: Request) -> Response:
        """Process a question and return an answer with citations."""
        serializer = QuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        topic_id = serializer.validated_data["topic_id"]
        question = serializer.validated_data["question"]

        # Use RAG pipeline to generate answer
        try:
            rag_service = RAGService()
            result = rag_service.query(query=question, topic_ids=[topic_id])

            # Format citations from sources
            citations = [
                {
                    "title": source["title"],
                    "content": source["content"][:200] + "..."
                    if len(source["content"]) > 200
                    else source["content"],
                    "score": source["score"],
                    "context_type": source["context_type"],
                    "context_item_id": source["context_item_id"],
                }
                for source in result["sources"]
            ]

            return Response(
                {
                    "answer": result["answer"],
                    "citations": citations,
                    "topic_id": topic_id,
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            # Handle validation errors from RAG service
            logger.warning("RAG validation error: %s", str(e))

            return Response(
                {"error": "Invalid request parameters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except ConnectionError as e:
            # Handle external service connection errors
            logger.error("RAG connection error: %s", str(e))

            return Response(
                {
                    "error": "Unable to connect to external services. Please try again later.",
                    "detail": "The system is temporarily unavailable.",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        except Exception as e:
            # Log the error for debugging
            logger.error("RAG pipeline error: %s", str(e), exc_info=True)

            # Return user-friendly error message
            return Response(
                {
                    "error": "An error occurred while processing your question. Please try again.",
                    "detail": "If the problem persists, please contact support.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Template-based views for web interface


class TopicSelectionView(TemplateView):
    """View for displaying topic selection page."""

    template_name = "rag/topic_selection.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add topics to the template context."""
        context = super().get_context_data(**kwargs)
        context["topics"] = Topic.objects.all()
        return context


class QAInterfaceRedirectView(TemplateView):
    """Redirect view for Q&A interface without topic ID."""

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Redirect to topic selection page."""
        return redirect(reverse("rag_web:topic-selection"))


class QAInterfaceView(TemplateView):
    """View for displaying Q&A interface with selected topic."""

    template_name = "rag/qa_interface.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add topic to the template context."""
        context = super().get_context_data(**kwargs)
        context["topic"] = get_object_or_404(Topic, id=kwargs["topic_id"])
        return context
