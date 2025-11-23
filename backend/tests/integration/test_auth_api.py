"""
Integration tests for authentication API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User


class TestAuthAPI:
    """Tests for /api/v1/auth endpoints."""

    def test_register_user_success(self, client: TestClient):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "full_name": "New User",
                "password": "SecurePass123!",
                "role": "researcher",
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "password" not in data
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration with duplicate email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "username": "different",
                "password": "SecurePass123!",
            }
        )

        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()

    def test_register_weak_password(self, client: TestClient):
        """Test registration with weak password."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "weak",
            }
        )

        assert response.status_code == 400

    def test_login_success(self, client: TestClient, test_user: User, test_password: str):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": test_password,
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_with_email(self, client: TestClient, test_user: User, test_password: str):
        """Test login using email instead of username."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.email,  # Using email
                "password": test_password,
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_wrong_password(self, client: TestClient, test_user: User):
        """Test login with wrong password."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "WrongPassword123!",
            }
        )

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with nonexistent user."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "Password123!",
            }
        )

        assert response.status_code == 401

    def test_get_current_user(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test getting current user information."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert "password" not in data

    def test_get_current_user_no_token(self, client: TestClient):
        """Test getting current user without token."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 403  # No credentials provided

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401

    def test_change_password_success(
        self,
        client: TestClient,
        test_user: User,
        auth_headers: dict,
        test_password: str
    ):
        """Test successful password change."""
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "old_password": test_password,
                "new_password": "NewSecurePass456!",
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        assert "success" in response.json()["message"].lower()

    def test_change_password_wrong_old(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test password change with wrong old password."""
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "old_password": "WrongOldPass123!",
                "new_password": "NewSecurePass456!",
            },
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "incorrect" in response.json()["detail"].lower()

    def test_refresh_token(self, client: TestClient, auth_headers: dict):
        """Test token refresh."""
        response = client.post("/api/v1/auth/refresh", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_logout(self, client: TestClient, auth_headers: dict):
        """Test logout."""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)

        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()
