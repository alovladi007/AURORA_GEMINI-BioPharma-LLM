"""
Unit tests for UserService.
"""

import pytest
from sqlalchemy.orm import Session

from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User, UserRole


class TestUserService:
    """Tests for UserService class."""

    def test_create_user_success(self, db_session: Session):
        """Test successful user creation."""
        service = UserService(db_session)
        user_data = UserCreate(
            email="new@example.com",
            username="newuser",
            full_name="New User",
            password="SecurePass123!",
            role=UserRole.RESEARCHER,
        )

        user, error = service.create_user(user_data)

        assert error is None
        assert user is not None
        assert user.email == "new@example.com"
        assert user.username == "newuser"
        assert user.full_name == "New User"
        assert user.role == UserRole.RESEARCHER
        assert user.is_active is True
        assert user.hashed_password != "SecurePass123!"  # Should be hashed

    def test_create_user_duplicate_email(self, db_session: Session, test_user: User):
        """Test user creation with duplicate email."""
        service = UserService(db_session)
        user_data = UserCreate(
            email=test_user.email,  # Duplicate
            username="different",
            password="SecurePass123!",
        )

        user, error = service.create_user(user_data)

        assert user is None
        assert error is not None
        assert "email" in error.lower()

    def test_create_user_duplicate_username(self, db_session: Session, test_user: User):
        """Test user creation with duplicate username."""
        service = UserService(db_session)
        user_data = UserCreate(
            email="different@example.com",
            username=test_user.username,  # Duplicate
            password="SecurePass123!",
        )

        user, error = service.create_user(user_data)

        assert user is None
        assert error is not None
        assert "username" in error.lower()

    def test_create_user_weak_password(self, db_session: Session):
        """Test user creation with weak password."""
        service = UserService(db_session)
        user_data = UserCreate(
            email="new@example.com",
            username="newuser",
            password="weak",  # Too short, no uppercase, no numbers
        )

        user, error = service.create_user(user_data)

        assert user is None
        assert error is not None

    def test_get_user_by_id(self, db_session: Session, test_user: User):
        """Test getting user by ID."""
        service = UserService(db_session)
        user = service.get_user_by_id(test_user.id)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    def test_get_user_by_email(self, db_session: Session, test_user: User):
        """Test getting user by email."""
        service = UserService(db_session)
        user = service.get_user_by_email(test_user.email)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    def test_get_user_by_username(self, db_session: Session, test_user: User):
        """Test getting user by username."""
        service = UserService(db_session)
        user = service.get_user_by_username(test_user.username)

        assert user is not None
        assert user.id == test_user.id
        assert user.username == test_user.username

    def test_authenticate_user_success(self, db_session: Session, test_user: User, test_password: str):
        """Test successful user authentication."""
        service = UserService(db_session)
        user = service.authenticate_user(test_user.username, test_password)

        assert user is not None
        assert user.id == test_user.id

    def test_authenticate_user_wrong_password(self, db_session: Session, test_user: User):
        """Test authentication with wrong password."""
        service = UserService(db_session)
        user = service.authenticate_user(test_user.username, "WrongPassword123!")

        assert user is None

    def test_authenticate_user_nonexistent(self, db_session: Session):
        """Test authentication of nonexistent user."""
        service = UserService(db_session)
        user = service.authenticate_user("nonexistent", "password")

        assert user is None

    def test_update_user(self, db_session: Session, test_user: User):
        """Test updating user information."""
        service = UserService(db_session)
        update_data = UserUpdate(
            full_name="Updated Name",
            role=UserRole.ADMIN,
        )

        updated_user, error = service.update_user(test_user.id, update_data)

        assert error is None
        assert updated_user is not None
        assert updated_user.full_name == "Updated Name"
        assert updated_user.role == UserRole.ADMIN

    def test_change_password_success(self, db_session: Session, test_user: User, test_password: str):
        """Test successful password change."""
        service = UserService(db_session)
        new_password = "NewSecurePass456!"

        success, error = service.change_password(
            test_user.id,
            test_password,
            new_password
        )

        assert success is True
        assert error is None

        # Verify new password works
        user = service.authenticate_user(test_user.username, new_password)
        assert user is not None

    def test_change_password_wrong_old_password(self, db_session: Session, test_user: User):
        """Test password change with wrong old password."""
        service = UserService(db_session)

        success, error = service.change_password(
            test_user.id,
            "WrongOldPass123!",
            "NewSecurePass456!"
        )

        assert success is False
        assert error is not None
        assert "incorrect" in error.lower()

    def test_delete_user(self, db_session: Session, test_user: User):
        """Test user deletion (soft delete)."""
        service = UserService(db_session)
        result = service.delete_user(test_user.id)

        assert result is True

        # User should still exist but be inactive
        user = service.get_user_by_id(test_user.id)
        assert user is not None
        assert user.is_active is False
