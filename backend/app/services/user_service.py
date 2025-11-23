"""
User service for managing user accounts.

Handles user CRUD operations, authentication, and authorization.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password, validate_password_strength


class UserService:
    """Service for user management operations."""

    def __init__(self, db: Session):
        """
        Initialize user service.

        Args:
            db: Database session
        """
        self.db = db

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User object or None if not found
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email: Email address

        Returns:
            User object or None if not found
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            username: Username

        Returns:
            User object or None if not found
        """
        return self.db.query(User).filter(User.username == username).first()

    def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
    ) -> List[User]:
        """
        Get list of users with optional filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            role: Filter by user role
            is_active: Filter by active status

        Returns:
            List of users
        """
        query = self.db.query(User)

        if role is not None:
            query = query.filter(User.role == role)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        return query.offset(skip).limit(limit).all()

    def create_user(self, user_data: UserCreate) -> tuple[Optional[User], Optional[str]]:
        """
        Create a new user.

        Args:
            user_data: User creation data

        Returns:
            Tuple of (User object, error_message)
        """
        # Validate password strength
        is_valid, error_msg = validate_password_strength(user_data.password)
        if not is_valid:
            return None, error_msg

        # Check if email already exists
        if self.get_user_by_email(user_data.email):
            return None, "Email already registered"

        # Check if username already exists
        if self.get_user_by_username(user_data.username):
            return None, "Username already taken"

        try:
            # Create user with hashed password
            db_user = User(
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                hashed_password=get_password_hash(user_data.password),
                role=user_data.role,
                is_active=True,
                is_verified=False,
            )

            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)

            return db_user, None

        except IntegrityError as e:
            self.db.rollback()
            return None, f"Database error: {str(e)}"

    def update_user(
        self,
        user_id: int,
        user_data: UserUpdate,
    ) -> tuple[Optional[User], Optional[str]]:
        """
        Update user information.

        Args:
            user_id: User ID
            user_data: Updated user data

        Returns:
            Tuple of (Updated user object, error_message)
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None, "User not found"

        # Check email uniqueness if being updated
        if user_data.email and user_data.email != user.email:
            if self.get_user_by_email(user_data.email):
                return None, "Email already registered"

        # Check username uniqueness if being updated
        if user_data.username and user_data.username != user.username:
            if self.get_user_by_username(user_data.username):
                return None, "Username already taken"

        try:
            # Update only provided fields
            update_data = user_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user, field, value)

            self.db.commit()
            self.db.refresh(user)

            return user, None

        except IntegrityError as e:
            self.db.rollback()
            return None, f"Database error: {str(e)}"

    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user (soft delete by setting is_active=False).

        Args:
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        # Soft delete
        user.is_active = False
        self.db.commit()

        return True

    def authenticate_user(
        self,
        username: str,
        password: str,
    ) -> Optional[User]:
        """
        Authenticate user with username and password.

        Args:
            username: Username or email
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        # Try to find user by username or email
        user = self.get_user_by_username(username)
        if not user:
            user = self.get_user_by_email(username)

        if not user:
            return None

        # Verify password
        if not verify_password(password, user.hashed_password):
            return None

        # Check if user is active
        if not user.is_active:
            return None

        return user

    def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str,
    ) -> tuple[bool, Optional[str]]:
        """
        Change user password.

        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password

        Returns:
            Tuple of (success, error_message)
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False, "User not found"

        # Verify old password
        if not verify_password(old_password, user.hashed_password):
            return False, "Incorrect current password"

        # Validate new password strength
        is_valid, error_msg = validate_password_strength(new_password)
        if not is_valid:
            return False, error_msg

        # Update password
        user.hashed_password = get_password_hash(new_password)
        self.db.commit()

        return True, None

    def verify_user_email(self, user_id: int) -> bool:
        """
        Mark user email as verified.

        Args:
            user_id: User ID

        Returns:
            True if verified, False if user not found
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        user.is_verified = True
        self.db.commit()

        return True
