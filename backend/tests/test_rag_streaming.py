"""Tests for RAG streaming endpoint - integration tests."""

import pytest


class TestRAGStreamingEndpoint:
    """Test SSE streaming endpoint - schema and basic functionality."""

    def test_stream_request_schema_validation(self) -> None:
        """StreamQuestionRequest should validate required fields properly."""
        from pydantic import ValidationError

        from backend.schemas.rag import StreamQuestionRequest

        with pytest.raises(ValidationError):
            StreamQuestionRequest(topic_id=-1, question="", session_id="")

        with pytest.raises(ValidationError):
            StreamQuestionRequest(topic_id=0, question="Test", session_id="abc")

        valid = StreamQuestionRequest(
            topic_id=1, question="Test question?", session_id="test-session-123"
        )
        assert valid.topic_id == 1
        assert valid.question == "Test question?"
        assert valid.session_id == "test-session-123"

    def test_streaming_endpoint_registered(self) -> None:
        """Streaming endpoint should be registered in app routes."""
        from starlette.routing import Route

        from backend.main import app

        route_paths = [route.path for route in app.routes if isinstance(route, Route)]
        assert "/api/rag/stream" in route_paths
