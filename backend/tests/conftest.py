"""Shared test fixtures for FastAPI tests."""

import json
import os
from pathlib import Path
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.auth.utils import pwd_context
from backend.main import app
from backend.models import User as SQLUser
from backend.models.base import Base, get_db

WORKER_ID = os.environ.get("PYTEST_XDIST_WORKER")
DB_FILENAME = f"test_api_{WORKER_ID}.db" if WORKER_ID else "test_api.db"
SQLALCHEMY_TEST_DATABASE_URL = f"sqlite:///./{DB_FILENAME}"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine, checkfirst=True)


def override_get_db():
    """Override FastAPI database dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Teardown test database at session end."""
    yield
    Base.metadata.drop_all(bind=engine, checkfirst=True)
    Path(DB_FILENAME).unlink(missing_ok=True)


@pytest.fixture(scope="function")
def db_session():
    """Provide a clean database session for each test."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            try:
                db.execute(table.delete())
            except Exception:
                pass
        db.commit()
        db.close()


@pytest.fixture(scope="function")
def admin_headers(db_session):
    """Create an admin user and return Authorization headers."""
    client = TestClient(app)
    password = "AdminPass123"
    admin = SQLUser(
        username="admin",
        email="admin@example.com",
        password=pwd_context.hash(password),
        is_active=True,
        is_staff=True,
        is_superuser=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    response = client.post(
        "/api/auth/login",
        data={"username": cast(str, admin.username), "password": password},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def client():
    """Provide a TestClient for FastAPI app."""
    return TestClient(app)


@pytest.fixture(scope="function")
def redis_client():
    """Provide Redis client for integration tests."""
    import redis

    from backend.config import settings

    client = redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    try:
        # Verify Redis is available
        client.ping()
        yield client
    except redis.ConnectionError:
        pytest.skip("Redis not available for integration tests")
    finally:
        client.close()


@pytest.fixture(scope="session")
def golden_dataset():
    """Load golden dataset for accuracy tests."""
    dataset_path = Path(__file__).parent / "fixtures" / "golden_dataset.json"
    with open(dataset_path) as f:
        return json.load(f)


@pytest.fixture(scope="function")
def integration_db_with_golden_data(golden_dataset):
    """
    Provides database with golden dataset contexts and embeddings for integration tests.

    Requires: Redis and Qdrant services running (docker-compose.dev.yml)

    WARNING: This fixture creates records with explicit IDs (1, 2, 3...) in the
    production/dev database. To avoid data conflicts, ensure you clean up before
    running tests or use a dedicated test database (scholaria_test).
    """
    import json
    from typing import Any

    from qdrant_client.models import PointStruct

    from backend.config import settings
    from backend.models import Context, ContextItem, Topic
    from backend.models.base import SessionLocal, _ensure_engine
    from backend.retrieval.embeddings import EmbeddingService
    from backend.retrieval.qdrant import QdrantService

    if not settings.OPENAI_API_KEY:
        pytest.skip("OpenAI API key not configured for integration tests")

    _ensure_engine()

    db_session = SessionLocal()

    fixture_path = Path(__file__).parent / "fixtures" / "fake_contexts_data.json"
    with open(fixture_path) as f:
        fake_contexts_raw = json.load(f)
    fake_contexts_data: dict[int, dict[str, Any]] = {
        int(k): v for k, v in fake_contexts_raw.items()
    }

    try:
        db_session.query(ContextItem).filter(
            ContextItem.id.in_(list(fake_contexts_data.keys()))
        ).delete(synchronize_session=False)

        existing_topics = db_session.query(Topic).filter(Topic.id.in_([1, 2, 3])).all()
        for topic in existing_topics:
            for context in topic.contexts:
                db_session.delete(context)
            db_session.delete(topic)

        db_session.commit()
    except Exception:
        db_session.rollback()

    try:
        qdrant_service = QdrantService()
        qdrant_service.client.get_collection(qdrant_service.collection_name)
    except Exception:
        pytest.skip("Qdrant service not available for integration tests")

    embedding_service = EmbeddingService()

    created_topic_ids: list[int] = []
    topics: dict[int, Topic] = {}
    for topic_id in [1, 2, 3]:
        topic = Topic(
            id=topic_id,
            name=f"Topic {topic_id}",
            slug=f"topic-{topic_id}",
            description=f"Test topic {topic_id} for golden dataset integration",
        )
        db_session.add(topic)
        topics[topic_id] = topic
        created_topic_ids.append(topic_id)
    db_session.commit()

    created_context_ids: list[int] = []
    context_item_ids_created: list[int] = []
    for context_item_id, data in fake_contexts_data.items():
        context = Context(
            name=str(data["title"]),
            description=f"Test context {context_item_id} for golden dataset",
            context_type="markdown",
            original_content=str(data["content"]),
            chunk_count=1,
            processing_status="completed",
        )
        db_session.add(context)
        db_session.flush()
        created_context_ids.append(context.id)

        topic_id_for_context = int(data["topic_id"])
        context.topics.append(topics[topic_id_for_context])

        context_item = ContextItem(
            id=context_item_id,
            context_id=context.id,
            title=str(data["title"]),
            content=str(data["content"]),
            order_index=0,
        )
        db_session.add(context_item)
        db_session.flush()

        embedding = embedding_service.generate_embedding(str(data["content"]))

        payload = {
            "context_item_id": context_item_id,
            "title": str(data["title"]),
            "content": str(data["content"]),
            "context_id": context.id,
            "context_type": "markdown",
        }

        point = PointStruct(id=context_item_id, vector=embedding, payload=payload)
        qdrant_service.client.upsert(
            collection_name=qdrant_service.collection_name, points=[point]
        )

        context_item_ids_created.append(context_item_id)

    db_session.commit()

    yield db_session

    try:
        if context_item_ids_created:
            try:
                qdrant_service.client.delete(
                    collection_name=qdrant_service.collection_name,
                    points_selector=context_item_ids_created,
                )
            except Exception:
                pass

        db_session.query(ContextItem).filter(
            ContextItem.id.in_(context_item_ids_created)
        ).delete(synchronize_session=False)

        db_session.query(Context).filter(Context.id.in_(created_context_ids)).delete(
            synchronize_session=False
        )

        db_session.query(Topic).filter(Topic.id.in_(created_topic_ids)).delete(
            synchronize_session=False
        )

        db_session.commit()
    except Exception:
        db_session.rollback()
    finally:
        db_session.close()
