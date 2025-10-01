"""
POC tests for FastAPI Topics endpoint.

Tests GET /api/topics endpoint against Django database.
"""

import pytest
from fastapi.testclient import TestClient
from rest_framework.test import APIClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.models.base import get_db


@pytest.fixture
def test_db():
    """Create test database connection using Django's database."""
    from django.conf import settings

    db_config = settings.DATABASES["default"]
    database_url = f"postgresql+psycopg://{db_config['USER']}:{db_config['PASSWORD']}@{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}"

    engine = create_engine(database_url)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Override get_db dependency
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestingSessionLocal

    app.dependency_overrides.clear()


@pytest.fixture
def client(test_db):
    """FastAPI test client."""
    return TestClient(app)


def assert_nested_equal(left: list[dict], right: list[dict]) -> None:
    """Recursively compare topic payloads allowing topic-level reordering by id."""

    left_sorted = sorted(left, key=lambda item: item["id"])
    right_sorted = sorted(right, key=lambda item: item["id"])
    assert len(left_sorted) == len(right_sorted)

    for fastapi_topic, django_topic in zip(left_sorted, right_sorted, strict=True):
        assert fastapi_topic["id"] == django_topic["id"]
        assert fastapi_topic == django_topic


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_list_topics_empty(client):
    """Test listing topics returns empty list when no topics exist."""
    response = client.get("/api/topics")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.django_db(transaction=True)
def test_list_topics_with_data(client):
    """Test listing topics returns data from Django database."""
    from django.db import transaction

    from backend.models import Context, Topic

    # Create test data using Django ORM with explicit transaction
    with transaction.atomic():
        context = Context.objects.create(
            name="Test Context POC",
            description="Context Description POC",
            context_type="PDF",
        )
        topic = Topic.objects.create(
            name="Test Topic POC",
            description="Test Description POC",
        )
        topic.contexts.add(context)
        topic_id = topic.id
        context_id = context.id

    try:
        response = client.get("/api/topics")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

        # Find our test topic
        test_topic = next((t for t in data if t["id"] == topic_id), None)
        assert test_topic is not None
        assert test_topic["name"] == "Test Topic POC"
        assert test_topic["description"] == "Test Description POC"
        assert "created_at" in test_topic
        assert "updated_at" in test_topic
        assert "contexts" in test_topic
        assert isinstance(test_topic["contexts"], list)
        linked_context = next(
            (c for c in test_topic["contexts"] if c["id"] == context_id), None
        )
        assert linked_context is not None
        assert linked_context["name"] == "Test Context POC"
        assert linked_context["context_type"] == "PDF"
    finally:
        # Cleanup
        Topic.objects.filter(id=topic_id).delete()
        Context.objects.filter(id=context_id).delete()


@pytest.mark.django_db(transaction=True)
def test_get_topic_by_id(client):
    """Test getting a single topic by ID."""
    from django.db import transaction

    from backend.models import Context, Topic

    # Create test data with explicit transaction
    with transaction.atomic():
        context = Context.objects.create(
            name="Single Context POC",
            description="Single Context Description",
            context_type="FAQ",
        )
        topic = Topic.objects.create(
            name="Single Topic POC",
            description="Single Description POC",
        )
        topic.contexts.add(context)
        topic_id = topic.id
        context_id = context.id

    try:
        response = client.get(f"/api/topics/{topic_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == topic_id
        assert data["name"] == "Single Topic POC"
        assert data["description"] == "Single Description POC"
        assert "contexts" in data
        assert isinstance(data["contexts"], list)
        linked_context = next(
            (c for c in data["contexts"] if c["id"] == context_id), None
        )
        assert linked_context is not None
        assert linked_context["context_type"] == "FAQ"
    finally:
        # Cleanup
        Topic.objects.filter(id=topic_id).delete()
        Context.objects.filter(id=context_id).delete()


def test_get_topic_not_found(client):
    """Test getting a non-existent topic returns 404."""
    response = client.get("/api/topics/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Topic not found"


@pytest.mark.django_db(transaction=True)
def test_topics_response_matches_django(client):
    """FastAPI /api/topics payload mirrors Django topics endpoint."""
    from django.db import transaction
    from django.urls import reverse

    from backend.models import Context, Topic

    django_client = APIClient()

    with transaction.atomic():
        context_a = Context.objects.create(
            name="Algebra Context",
            description="Algebra overview",
            context_type="FAQ",
        )
        context_b = Context.objects.create(
            name="Geometry Context",
            description="Geometry overview",
            context_type="PDF",
        )
        topic = Topic.objects.create(
            name="Mathematics",
            description="Math topics",
            system_prompt="You are a math tutor.",
        )
        topic.contexts.add(context_b, context_a)

    fastapi_response = client.get("/api/topics")
    django_response = django_client.get(reverse("rag:topics"))

    assert fastapi_response.status_code == 200
    assert django_response.status_code == 200

    fastapi_payload = fastapi_response.json()
    django_payload = django_response.json()

    assert_nested_equal(fastapi_payload, django_payload)


@pytest.mark.django_db(transaction=True)
def test_topic_detail_response_matches_django(client):
    """FastAPI topic detail mirrors Django topic detail payload."""
    from django.db import transaction
    from django.urls import reverse

    from backend.models import Context, Topic

    django_client = APIClient()

    with transaction.atomic():
        context = Context.objects.create(
            name="Chemistry Context",
            description="Chemistry basics",
            context_type="MARKDOWN",
        )
        topic = Topic.objects.create(
            name="Science",
            description="Science topics",
            system_prompt="You are a science tutor.",
        )
        topic.contexts.add(context)
        topic_id = topic.id

    fastapi_response = client.get(f"/api/topics/{topic_id}")
    django_response = django_client.get(reverse("rag:topic-detail", args=[topic_id]))

    assert fastapi_response.status_code == 200
    assert django_response.status_code == 200
    assert fastapi_response.json() == django_response.json()


def test_topics_endpoint_disallows_write_methods(client):
    """Ensure POST/PUT/DELETE return 405 for read-only POC."""
    for method in ["post", "put", "delete"]:
        response = getattr(client, method)("/api/topics")
        assert response.status_code == 405
