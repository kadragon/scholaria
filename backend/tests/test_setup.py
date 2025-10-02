"""Test initial setup endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.auth.utils import pwd_context
from backend.main import app
from backend.models.user import User

client = TestClient(app)


class TestSetupCheck:
    def test_check_needs_setup_when_no_admin(self, db_session) -> None:
        response = client.get("/api/setup/check")

        assert response.status_code == 200
        data = response.json()
        assert data["needs_setup"] is True
        assert data["admin_exists"] is False

    def test_check_no_setup_when_admin_exists(self, db_session) -> None:
        admin = User(
            username="admin",
            email="admin@test.com",
            password=pwd_context.hash("testpass123"),
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        db_session.add(admin)
        db_session.commit()

        response = client.get("/api/setup/check")

        assert response.status_code == 200
        data = response.json()
        assert data["needs_setup"] is False
        assert data["admin_exists"] is True


class TestInitialAdminCreation:
    def test_create_initial_admin_success(self, db_session) -> None:
        response = client.post(
            "/api/setup/init",
            json={
                "username": "admin",
                "email": "admin@scholaria.com",
                "password": "securepass123",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "message" in data
        assert "created successfully" in data["message"]

        admin = db_session.query(User).filter(User.username == "admin").first()
        assert admin is not None
        assert admin.is_staff is True
        assert admin.is_superuser is True
        assert admin.is_active is True
        assert pwd_context.verify("securepass123", admin.password)

    def test_create_initial_admin_fails_when_admin_exists(self, db_session) -> None:
        existing_admin = User(
            username="existing",
            email="existing@test.com",
            password=pwd_context.hash("pass123"),
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        db_session.add(existing_admin)
        db_session.commit()

        response = client.post(
            "/api/setup/init",
            json={
                "username": "newadmin",
                "email": "new@test.com",
                "password": "newpass123",
            },
        )

        assert response.status_code == 403
        assert "already exists" in response.json()["detail"]

    def test_create_initial_admin_duplicate_username(self, db_session) -> None:
        user = User(
            username="testuser",
            email="test@test.com",
            password=pwd_context.hash("pass123"),
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )
        db_session.add(user)
        db_session.commit()

        response = client.post(
            "/api/setup/init",
            json={
                "username": "testuser",
                "email": "admin@test.com",
                "password": "adminpass123",
            },
        )

        assert response.status_code == 400
        assert "Username already exists" in response.json()["detail"]

    def test_create_initial_admin_duplicate_email(self, db_session) -> None:
        user = User(
            username="testuser",
            email="test@test.com",
            password=pwd_context.hash("pass123"),
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )
        db_session.add(user)
        db_session.commit()

        response = client.post(
            "/api/setup/init",
            json={
                "username": "admin",
                "email": "test@test.com",
                "password": "adminpass123",
            },
        )

        assert response.status_code == 400
        assert "Email already exists" in response.json()["detail"]

    def test_create_initial_admin_validation_short_username(self, db_session) -> None:
        response = client.post(
            "/api/setup/init",
            json={
                "username": "ab",
                "email": "admin@test.com",
                "password": "adminpass123",
            },
        )

        assert response.status_code == 422

    def test_create_initial_admin_validation_short_password(self, db_session) -> None:
        response = client.post(
            "/api/setup/init",
            json={
                "username": "admin",
                "email": "admin@test.com",
                "password": "short",
            },
        )

        assert response.status_code == 422

    def test_create_initial_admin_validation_invalid_email(self, db_session) -> None:
        response = client.post(
            "/api/setup/init",
            json={
                "username": "admin",
                "email": "notanemail",
                "password": "adminpass123",
            },
        )

        assert response.status_code == 422
