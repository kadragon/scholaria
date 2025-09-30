"""Shared test fixtures for FastAPI tests."""

import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from api.models.base import Base, get_db

WORKER_ID = os.environ.get("PYTEST_XDIST_WORKER")
DB_FILENAME = f"test_api_{WORKER_ID}.db" if WORKER_ID else "test_api.db"
SQLALCHEMY_TEST_DATABASE_URL = f"sqlite:///./{DB_FILENAME}"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
    """Create all tables in test database at session start."""
    Base.metadata.create_all(bind=engine, checkfirst=True)
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
