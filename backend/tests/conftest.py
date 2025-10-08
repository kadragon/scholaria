"""Shared test fixtures for FastAPI tests."""

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
    import json

    dataset_path = Path(__file__).parent / "fixtures" / "golden_dataset.json"
    with open(dataset_path) as f:
        return json.load(f)
