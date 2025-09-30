"""Tests for authentication endpoints and utilities."""

import importlib

import pytest
from django.contrib.auth.models import User
from fastapi.testclient import TestClient

import api.auth.utils as auth_utils
import api.config as config_module
from api.main import app
from api.models.user import User as SQLUser

client = TestClient(app)


@pytest.fixture(autouse=True)
def _reset_auth_utils(monkeypatch: pytest.MonkeyPatch):
    """Ensure auth utils use fresh settings for each test."""

    for key in ("JWT_SECRET_KEY", "JWT_ALGORITHM", "JWT_ACCESS_TOKEN_EXPIRE_HOURS"):
        monkeypatch.delenv(key, raising=False)

    importlib.reload(config_module)
    importlib.reload(auth_utils)
    yield
    importlib.reload(config_module)
    importlib.reload(auth_utils)


class TestAuthUtils:
    """Test authentication utility functions."""

    def test_verify_django_password(self) -> None:
        """Test Django password verification."""
        user = User(username="test")
        user.set_password("testpass123")
        assert auth_utils.verify_password("testpass123", user.password)
        assert not auth_utils.verify_password("wrongpass", user.password)

    def test_create_and_decode_token(self) -> None:
        """Test JWT token creation and decoding."""
        token = auth_utils.create_access_token(data={"sub": "123"})
        payload = auth_utils.decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "123"
        assert "exp" in payload

    def test_decode_invalid_token(self) -> None:
        """Test decoding invalid JWT token."""
        result = auth_utils.decode_access_token("invalid.token.here")
        assert result is None

    def test_auth_utils_use_settings(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Auth utils should respect JWT settings sourced from environment."""
        monkeypatch.setenv("JWT_SECRET_KEY", "unit-test-secret")
        monkeypatch.setenv("JWT_ALGORITHM", "HS512")
        monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRE_HOURS", "2")

        config = importlib.reload(config_module)
        settings = config.Settings()

        reloaded_utils = importlib.reload(auth_utils)

        assert settings.JWT_SECRET_KEY == "unit-test-secret"
        assert settings.JWT_ALGORITHM == "HS512"
        assert settings.JWT_ACCESS_TOKEN_EXPIRE_HOURS == 2

        assert reloaded_utils.SECRET_KEY == settings.JWT_SECRET_KEY
        assert reloaded_utils.ALGORITHM == settings.JWT_ALGORITHM
        assert (
            reloaded_utils.ACCESS_TOKEN_EXPIRE_HOURS
            == settings.JWT_ACCESS_TOKEN_EXPIRE_HOURS
        )

        token = reloaded_utils.create_access_token(data={"sub": "abc"})
        payload = reloaded_utils.decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "abc"


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_login_success(self, db_session) -> None:
        """Test successful login returns JWT token."""
        user = SQLUser(
            username="testuser",
            password=auth_utils.pwd_context.hash("testpass123"),
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        response = client.post(
            "/api/auth/login",
            data={"username": "testuser", "password": "testpass123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self) -> None:
        """Test login with invalid credentials."""
        response = client.post(
            "/api/auth/login",
            data={"username": "nonexistent", "password": "wrongpass"},
        )

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_inactive_user(self, db_session) -> None:
        """Test login with inactive user."""
        user = SQLUser(
            username="inactive",
            password=auth_utils.pwd_context.hash("testpass123"),
            is_active=False,
        )
        db_session.add(user)
        db_session.commit()

        response = client.post(
            "/api/auth/login",
            data={"username": "inactive", "password": "testpass123"},
        )

        assert response.status_code == 403
        assert "Inactive user" in response.json()["detail"]

    def test_get_me_success(self, db_session) -> None:
        """Test /me endpoint with valid token."""
        user = SQLUser(
            username="testuser",
            password=auth_utils.pwd_context.hash("testpass123"),
            email="test@example.com",
            is_active=True,
            is_staff=True,
        )
        db_session.add(user)
        db_session.commit()

        login_response = client.post(
            "/api/auth/login",
            data={"username": "testuser", "password": "testpass123"},
        )
        token = login_response.json()["access_token"]

        response = client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["is_staff"] is True

    def test_get_me_no_token(self) -> None:
        """Test /me endpoint without token."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_get_me_invalid_token(self) -> None:
        """Test /me endpoint with invalid token."""
        response = client.get(
            "/api/auth/me", headers={"Authorization": "Bearer invalid.token"}
        )
        assert response.status_code == 401


class TestAuthDependencies:
    """Test authentication dependencies."""

    def test_require_admin_staff_user(self, db_session) -> None:
        """Test require_admin allows staff users."""
        user = SQLUser(
            username="admin",
            password=auth_utils.pwd_context.hash("adminpass"),
            is_active=True,
            is_staff=True,
        )
        db_session.add(user)
        db_session.commit()

        login_response = client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "adminpass"},
        )
        token = login_response.json()["access_token"]

        response = client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json()["is_staff"] is True

    def test_require_admin_superuser(self, db_session) -> None:
        """Test require_admin allows superusers."""
        user = SQLUser(
            username="superuser",
            password=auth_utils.pwd_context.hash("superpass"),
            email="super@example.com",
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()

        login_response = client.post(
            "/api/auth/login",
            data={"username": "superuser", "password": "superpass"},
        )
        token = login_response.json()["access_token"]

        response = client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_staff"] is True
        assert data["is_superuser"] is True
