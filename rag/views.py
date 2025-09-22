from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.serializers import (
    CharField,
    FloatField,
    IntegerField,
    ListField,
    ModelSerializer,
    Serializer,
)
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView

from .models import Context, ContextItem, Topic
from .retrieval.rag import RAGService

if TYPE_CHECKING:
    from django.db.models.query import QuerySet
    from django.http import HttpRequest, HttpResponse
    from rest_framework.request import Request


logger = logging.getLogger(__name__)


class ContextItemSerializer(ModelSerializer[ContextItem]):
    """Serializer for ContextItem model (chunks)."""

    class Meta:
        model = ContextItem
        fields = [
            "id",
            "title",
            "content",
            "context",
            "file_path",
            "metadata",
            "created_at",
            "updated_at",
        ]


class ContextSerializer(ModelSerializer[Context]):
    """Serializer for Context model with full content and metadata."""

    class Meta:
        model = Context
        fields = [
            "id",
            "name",
            "description",
            "context_type",
            "original_content",
            "chunk_count",
            "processing_status",
            "created_at",
            "updated_at",
        ]


class TopicSerializer(ModelSerializer[Topic]):
    """Serializer for Topic model with associated contexts."""

    contexts = ContextSerializer(many=True, read_only=True)

    class Meta:
        model = Topic
        fields = [
            "id",
            "name",
            "description",
            "system_prompt",
            "contexts",
            "created_at",
            "updated_at",
        ]


class CitationSerializer(Serializer[dict[str, str | float | int]]):
    """Serializer for citation information in responses."""

    title = CharField()
    content = CharField()
    score = FloatField()
    context_type = CharField()
    context_item_id = IntegerField()


class AnswerResponseSerializer(Serializer[dict[str, str | int | list[dict[str, Any]]]]):
    """Serializer for RAG answer responses."""

    answer = CharField()
    citations = ListField(child=CitationSerializer())
    topic_id = IntegerField()


class ErrorResponseSerializer(Serializer[dict[str, str]]):
    """Serializer for error responses."""

    error = CharField()
    detail = CharField(required=False)


@extend_schema_view(
    get=extend_schema(
        tags=["Topics"],
        summary="List all topics",
        description="Retrieve a list of all available academic topics for RAG queries.",
        responses={200: TopicSerializer(many=True)},
    )
)
class TopicListView(generics.ListAPIView[Topic]):
    """API endpoint for retrieving all topics."""

    serializer_class = TopicSerializer
    pagination_class = None  # Disable pagination for simple topic list

    def get_queryset(self) -> QuerySet[Topic]:
        """Return all topics with prefetched contexts to avoid N+1 queries."""
        return Topic.objects.prefetch_related("contexts").all()


@extend_schema_view(
    get=extend_schema(
        tags=["Topics"],
        summary="Get topic details",
        description="Retrieve detailed information about a specific academic topic by ID.",
        responses={
            200: TopicSerializer,
            404: ErrorResponseSerializer,
        },
    )
)
class TopicDetailView(generics.RetrieveAPIView[Topic]):
    """API endpoint for retrieving a single topic by ID."""

    serializer_class = TopicSerializer

    def get_queryset(self) -> QuerySet[Topic]:
        """Return all topics with prefetched contexts to avoid N+1 queries."""
        return Topic.objects.prefetch_related("contexts").all()


@extend_schema_view(
    get=extend_schema(
        tags=["Contexts"],
        summary="List all contexts",
        description="Retrieve a list of all available contexts with metadata.",
        responses={200: ContextSerializer(many=True)},
    )
)
class ContextListView(generics.ListAPIView[Context]):
    """API endpoint for retrieving all contexts."""

    serializer_class = ContextSerializer
    pagination_class = None  # Disable pagination for simple context list

    def get_queryset(self) -> QuerySet[Context]:
        """Return all contexts."""
        return Context.objects.all()


@extend_schema_view(
    get=extend_schema(
        tags=["Contexts"],
        summary="Get context details",
        description="Retrieve detailed information about a specific context by ID.",
        responses={
            200: ContextSerializer,
            404: ErrorResponseSerializer,
        },
    )
)
class ContextDetailView(generics.RetrieveAPIView[Context]):
    """API endpoint for retrieving a single context by ID."""

    serializer_class = ContextSerializer

    def get_queryset(self) -> QuerySet[Context]:
        """Return all contexts."""
        return Context.objects.all()


@extend_schema_view(
    get=extend_schema(
        tags=["Contexts"],
        summary="Get context chunks",
        description="Retrieve all chunks (context items) for a specific context. Internal use only.",
        responses={200: ContextItemSerializer(many=True)},
    )
)
class ContextChunksView(generics.ListAPIView[ContextItem]):
    """API endpoint for retrieving chunks (context items) of a specific context."""

    serializer_class = ContextItemSerializer
    pagination_class = None

    def get_queryset(self) -> QuerySet[ContextItem]:
        """Return context items for the specified context."""
        context_id = self.kwargs["context_id"]
        return ContextItem.objects.filter(context_id=context_id)


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


@extend_schema(
    tags=["RAG"],
    summary="Ask a question",
    description=(
        "Submit a question for a specific topic and receive an AI-generated answer "
        "with citations from relevant documents. Rate limited to 30 questions per minute."
    ),
    request=QuestionSerializer,
    responses={
        200: AnswerResponseSerializer,
        400: ErrorResponseSerializer,
        503: ErrorResponseSerializer,
        500: ErrorResponseSerializer,
    },
)
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


class HealthCheckView(APIView):
    """Simple health check endpoint for production monitoring."""

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        """Return health status of the application."""
        try:
            # Basic database connectivity check
            from django.db import connection

            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")

            # Check cache connectivity
            from django.core.cache import cache

            cache.set("health_check", "ok", 10)
            cache_status = cache.get("health_check") == "ok"

            if cache_status:
                return Response({"status": "healthy"}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"status": "unhealthy", "error": "Cache not accessible"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

        except Exception:
            # Log the error for debugging but don't expose internal details
            import logging

            logger = logging.getLogger(__name__)
            logger.exception("Health check failed")

            return Response(
                {"status": "unhealthy", "error": "Service unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
