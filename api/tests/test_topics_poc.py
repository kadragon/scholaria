"""
POC tests for FastAPI Topics endpoint.

Tests GET /api/topics endpoint against Django database.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from api.models.base import get_db


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

    from rag.models import Topic

    # Create test data using Django ORM with explicit transaction
    with transaction.atomic():
        topic = Topic.objects.create(
            name="Test Topic POC",
            description="Test Description POC",
        )
        topic_id = topic.id

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
    finally:
        # Cleanup
        Topic.objects.filter(id=topic_id).delete()


@pytest.mark.django_db(transaction=True)
def test_get_topic_by_id(client):
    """Test getting a single topic by ID."""
    from django.db import transaction

    from rag.models import Topic

    # Create test data with explicit transaction
    with transaction.atomic():
        topic = Topic.objects.create(
            name="Single Topic POC",
            description="Single Description POC",
        )
        topic_id = topic.id

    try:
        response = client.get(f"/api/topics/{topic_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == topic_id
        assert data["name"] == "Single Topic POC"
        assert data["description"] == "Single Description POC"
    finally:
        # Cleanup
        Topic.objects.filter(id=topic_id).delete()


def test_get_topic_not_found(client):
    """Test getting a non-existent topic returns 404."""
    response = client.get("/api/topics/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Topic not found"
