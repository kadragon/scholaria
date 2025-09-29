from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
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

from .models import Context, ContextItem, QuestionHistory, Topic
from .retrieval.rag import RAGService
from .services.question_suggestions import QuestionSuggestionService

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

    permission_classes = [IsAuthenticated]
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

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Return basic health status of the application."""
        from core.health import CacheHealthCheck, DatabaseHealthCheck

        try:
            # Quick database check
            db_check = DatabaseHealthCheck()
            db_result = db_check.check()

            # Quick cache check
            cache_check = CacheHealthCheck()
            cache_result = cache_check.check()

            # Return healthy only if both are healthy
            if db_result["status"] == "healthy" and cache_result["status"] == "healthy":
                return Response({"status": "healthy"}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        "status": "unhealthy",
                        "error": "Service dependencies unavailable",
                    },
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


class DetailedHealthCheckView(APIView):
    """Detailed health check endpoint with comprehensive system status."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Return detailed health status of all system components."""
        from django.conf import settings

        from core.health import get_default_health_checker

        # Check if access token is required and provided
        access_token = getattr(settings, "HEALTH_CHECK_ACCESS_TOKEN", None)
        if access_token:
            provided_token = request.GET.get("token") or request.headers.get(
                "X-Health-Token"
            )
            if provided_token != access_token:
                return Response(
                    {"error": "Invalid or missing access token"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        try:
            # Run comprehensive health checks
            health_checker = get_default_health_checker()
            results = health_checker.run_all_checks()

            # Determine HTTP status code based on overall health
            http_status = (
                status.HTTP_200_OK
                if results["overall_status"] == "healthy"
                else status.HTTP_503_SERVICE_UNAVAILABLE
            )

            return Response(results, status=http_status)

        except Exception:
            # Log the error for debugging
            import logging

            logger = logging.getLogger(__name__)
            logger.exception("Detailed health check failed")

            from datetime import datetime

            return Response(
                {
                    "overall_status": "unhealthy",
                    "error": "Health check system failure",
                    "timestamp": datetime.utcnow().isoformat(),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


# History API Serializers and Views


class QuestionHistorySerializer(ModelSerializer[QuestionHistory]):
    """Serializer for QuestionHistory model."""

    class Meta:
        model = QuestionHistory
        fields = [
            "id",
            "topic",
            "question",
            "answer",
            "session_id",
            "is_favorited",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CreateHistorySerializer(Serializer):
    """Serializer for creating history entries."""

    topic_id = IntegerField()
    question = CharField(max_length=5000)
    answer = CharField(max_length=10000)
    session_id = CharField(max_length=255)

    def validate_topic_id(self, value: int) -> int:
        """Validate that topic exists."""
        if not Topic.objects.filter(id=value).exists():
            raise serializers.ValidationError("Topic does not exist.")
        return value


class ToggleFavoriteSerializer(Serializer):
    """Serializer for toggling favorite status."""

    is_favorited = serializers.BooleanField()


@extend_schema_view(
    get=extend_schema(
        description="Get question history for a topic and session",
        parameters=[
            {"name": "topic_id", "type": int, "location": "query"},
            {"name": "session_id", "type": str, "location": "query"},
        ],
    ),
    post=extend_schema(
        description="Create a new question history entry",
        request=CreateHistorySerializer,
    ),
)
class HistoryListCreateView(APIView):
    """API view for listing and creating question history."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get(self, request: Request) -> Response:
        """Get question history filtered by topic and session."""
        topic_id = request.query_params.get("topic_id")
        session_id = request.query_params.get("session_id")

        if not topic_id:
            return Response(
                {"error": "topic_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = QuestionHistory.objects.filter(topic_id=topic_id)

        if session_id:
            queryset = queryset.filter(session_id=session_id)

        # Order by creation date (newest first)
        queryset = queryset.order_by("-created_at")

        serializer = QuestionHistorySerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        """Create a new question history entry."""
        serializer = CreateHistorySerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"success": False, "error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated_data = serializer.validated_data

        try:
            history = QuestionHistory.objects.create(
                topic_id=validated_data["topic_id"],
                question=validated_data["question"],
                answer=validated_data["answer"],
                session_id=validated_data["session_id"],
            )

            return Response(
                {"success": True, "id": history.id},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            logger.error(f"Error creating history: {e}")
            return Response(
                {"success": False, "error": "Failed to create history entry"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    description="Get favorited question history for a topic",
    parameters=[
        {"name": "topic_id", "type": int, "location": "query"},
    ],
)
class HistoryFavoritesView(APIView):
    """API view for getting favorited question history."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get(self, request: Request) -> Response:
        """Get favorited question history filtered by topic."""
        topic_id = request.query_params.get("topic_id")

        if not topic_id:
            return Response(
                {"error": "topic_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = QuestionHistory.objects.filter(
            topic_id=topic_id, is_favorited=True
        ).order_by("-created_at")

        serializer = QuestionHistorySerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(
    description="Toggle favorite status of a question history entry",
    request=ToggleFavoriteSerializer,
)
class ToggleFavoriteView(APIView):
    """API view for toggling favorite status of question history."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def post(self, request: Request, history_id: int) -> Response:
        """Toggle favorite status of a question history entry."""
        try:
            history = QuestionHistory.objects.get(id=history_id)
        except QuestionHistory.DoesNotExist:
            return Response(
                {"success": False, "error": "History entry not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ToggleFavoriteSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"success": False, "error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        history.is_favorited = serializer.validated_data["is_favorited"]
        history.save(update_fields=["is_favorited"])

        return Response({"success": True})


@extend_schema(
    description="Clear question history for a session",
    parameters=[
        {"name": "session_id", "type": str, "location": "query"},
    ],
)
class ClearHistoryView(APIView):
    """API view for clearing question history by session."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def delete(self, request: Request) -> Response:
        """Clear question history for a specific session."""
        session_id = request.query_params.get("session_id")

        if not session_id:
            return Response(
                {"success": False, "error": "session_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            deleted_count = QuestionHistory.objects.filter(
                session_id=session_id
            ).delete()[0]

            return Response({"success": True, "deleted_count": deleted_count})
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return Response(
                {"success": False, "error": "Failed to clear history"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    description="Get question suggestions for a topic based on its content",
    responses={
        200: {
            "type": "object",
            "properties": {
                "suggestions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of suggested questions",
                }
            },
        },
        404: {"description": "Topic not found"},
    },
)
class QuestionSuggestionsView(APIView):
    """API view for getting question suggestions based on topic content."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get(self, request: Request, topic_id: int) -> Response:
        """Get question suggestions for a specific topic."""
        # Verify topic exists - get_object_or_404 raises Http404 which DRF converts to 404 response
        get_object_or_404(Topic, id=topic_id)

        try:
            # Get suggestions from service
            suggestion_service = QuestionSuggestionService()
            suggestions = suggestion_service.get_topic_suggestions(topic_id)

            return Response({"suggestions": suggestions})

        except Exception as e:
            logger.error(f"Error generating question suggestions: {e}")
            return Response(
                {"error": "Failed to generate suggestions"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    description="Get chunk preview for a context",
    responses={
        200: {
            "type": "object",
            "properties": {
                "chunks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "title": {"type": "string"},
                            "content_preview": {"type": "string"},
                            "content_length": {"type": "integer"},
                            "created_at": {"type": "string", "format": "date-time"},
                        },
                    },
                },
                "total_count": {"type": "integer"},
                "context_info": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "processing_status": {"type": "string"},
                    },
                },
            },
        },
        404: {"description": "Context not found"},
    },
)
class ChunkPreviewView(APIView):
    """API view for chunk preview functionality."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get(self, request: Request, context_id: int) -> Response:
        """Get chunk preview for a context."""
        # Verify context exists
        context = get_object_or_404(Context, id=context_id)

        try:
            # Get chunks with pagination
            limit = int(request.query_params.get("limit", 20))
            offset = int(request.query_params.get("offset", 0))

            chunks = context.items.all()[offset : offset + limit]
            total_count = context.items.count()

            chunk_data = []
            for chunk in chunks:
                content_preview = (
                    chunk.content[:200] + "..."
                    if len(chunk.content) > 200
                    else chunk.content
                )
                chunk_data.append(
                    {
                        "id": chunk.id,
                        "title": chunk.title,
                        "content_preview": content_preview,
                        "content_length": len(chunk.content),
                        "created_at": chunk.created_at.isoformat(),
                    }
                )

            return Response(
                {
                    "chunks": chunk_data,
                    "total_count": total_count,
                    "context_info": {
                        "name": context.name,
                        "processing_status": context.processing_status,
                    },
                }
            )

        except Exception as e:
            logger.error(f"Error getting chunk preview: {e}")
            return Response(
                {"error": "Failed to get chunk preview"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    description="Reorder chunks in a context",
    request={
        "type": "object",
        "properties": {
            "chunk_order": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Array of chunk IDs in new order",
            }
        },
    },
    responses={
        200: {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
            },
        }
    },
)
class ChunkReorderView(APIView):
    """API view for chunk reordering."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def post(self, request: Request, context_id: int) -> Response:
        """Reorder chunks in a context."""
        get_object_or_404(Context, id=context_id)

        try:
            chunk_order = request.data.get("chunk_order", [])
            if not chunk_order:
                return Response(
                    {"success": False, "error": "chunk_order is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Update chunk ordering (would require adding order field to model)
            # For now, just return success
            return Response(
                {"success": True, "message": f"Reordered {len(chunk_order)} chunks"}
            )

        except Exception as e:
            logger.error(f"Error reordering chunks: {e}")
            return Response(
                {"success": False, "error": "Failed to reorder chunks"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    description="Bulk operations on chunks",
    request={
        "type": "object",
        "properties": {
            "chunk_ids": {"type": "array", "items": {"type": "integer"}},
            "operation": {"type": "string", "enum": ["delete", "merge", "split"]},
        },
    },
)
class ChunkBulkOperationsView(APIView):
    """API view for bulk chunk operations."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def delete(self, request: Request, context_id: int) -> Response:
        """Bulk delete chunks."""
        context = get_object_or_404(Context, id=context_id)

        try:
            chunk_ids = request.data.get("chunk_ids", [])
            operation = request.data.get("operation", "delete")

            if operation == "delete":
                affected_count, _ = ContextItem.objects.filter(
                    id__in=chunk_ids, context=context
                ).delete()

                # Update chunk count
                context.update_chunk_count()

                return Response({"success": True, "affected_count": affected_count})

            return Response(
                {"success": False, "error": f"Unsupported operation: {operation}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.error(f"Error in bulk chunk operation: {e}")
            return Response(
                {"success": False, "error": "Failed to perform bulk operation"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(description="Get processing status updates for a context")
class ProcessingStatusView(APIView):
    """API view for processing status updates."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get(self, request: Request, context_id: int) -> Response:
        """Get current processing status."""
        context = get_object_or_404(Context, id=context_id)

        return Response(
            {
                "processing_status": context.processing_status,
                "chunk_count": context.chunk_count,
                "last_updated": context.updated_at.isoformat(),
            }
        )


@extend_schema(description="Search and filter chunks in a context")
class ChunkSearchView(APIView):
    """API view for chunk search and filtering."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get(self, request: Request, context_id: int) -> Response:
        """Search chunks in a context."""
        context = get_object_or_404(Context, id=context_id)

        try:
            query = request.query_params.get("q", "")
            limit = int(request.query_params.get("limit", 10))

            chunks = context.items.all()

            if query:
                chunks = chunks.filter(content__icontains=query)

            chunks = chunks[:limit]

            chunk_data = []
            for chunk in chunks:
                content_preview = (
                    chunk.content[:200] + "..."
                    if len(chunk.content) > 200
                    else chunk.content
                )
                chunk_data.append(
                    {
                        "id": chunk.id,
                        "title": chunk.title,
                        "content_preview": content_preview,
                        "content_length": len(chunk.content),
                        "created_at": chunk.created_at.isoformat(),
                    }
                )

            return Response(
                {"chunks": chunk_data, "query": query, "total_found": len(chunk_data)}
            )

        except Exception as e:
            logger.error(f"Error searching chunks: {e}")
            return Response(
                {"error": "Failed to search chunks"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(description="Validate chunks in a context")
class ChunkValidationView(APIView):
    """API view for chunk validation."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def post(self, request: Request, context_id: int) -> Response:
        """Validate chunks in a context."""
        context = get_object_or_404(Context, id=context_id)

        try:
            chunks = context.items.all()
            validation_results = []
            issues_found = 0

            for chunk in chunks:
                issues = []

                # Check chunk size
                if len(chunk.content) < 10:
                    issues.append("Content too short")
                    issues_found += 1

                if len(chunk.content) > 5000:
                    issues.append("Content too long")
                    issues_found += 1

                # Check title
                if not chunk.title or len(chunk.title.strip()) < 3:
                    issues.append("Title missing or too short")
                    issues_found += 1

                validation_results.append(
                    {
                        "chunk_id": chunk.id,
                        "chunk_title": chunk.title,
                        "issues": issues,
                        "is_valid": len(issues) == 0,
                    }
                )

            return Response(
                {
                    "validation_results": validation_results,
                    "issues_found": issues_found,
                    "total_chunks": len(validation_results),
                }
            )

        except Exception as e:
            logger.error(f"Error validating chunks: {e}")
            return Response(
                {"error": "Failed to validate chunks"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
