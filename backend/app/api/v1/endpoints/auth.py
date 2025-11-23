"""
Authentication API endpoints.

Provides login, registration, token refresh, and password management.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token
from app.core.config import settings
from app.services.user_service import UserService
from app.schemas.user import (
    User as UserSchema,
    UserCreate,
    UserLogin,
    Token,
    PasswordChange,
)
from app.api.deps import get_current_user, get_current_user_id
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new user account.

    **Request Body:**
    - **email**: Valid email address (must be unique)
    - **username**: Username (3-100 characters, must be unique)
    - **password**: Password (min 8 characters, must include uppercase, lowercase, and number)
    - **full_name**: Optional full name
    - **role**: User role (default: researcher)

    **Returns:**
    - Created user object (without password)

    **Raises:**
    - 400: If email/username already exists or password is weak
    - 500: Database error
    """
    user_service = UserService(db)
    user, error = user_service.create_user(user_data)

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return user


@router.post("/login", response_model=Token)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Login with username/email and password.

    **Request Body:**
    - **username**: Username or email address
    - **password**: User password

    **Returns:**
    - JWT access token

    **Raises:**
    - 401: Invalid credentials or inactive account
    """
    user_service = UserService(db)
    user = user_service.authenticate_user(
        username=credentials.username,
        password=credentials.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires,
        additional_claims={"role": user.role.value},
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserSchema)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Get current authenticated user information.

    Requires authentication via Bearer token in Authorization header.

    **Returns:**
    - Current user object

    **Raises:**
    - 401: Invalid or missing authentication token
    - 404: User not found
    """
    return current_user


@router.post("/change-password")
def change_password(
    password_data: PasswordChange,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Change current user's password.

    Requires authentication via Bearer token in Authorization header.

    **Request Body:**
    - **old_password**: Current password
    - **new_password**: New password (min 8 characters, must include uppercase, lowercase, and number)

    **Returns:**
    - Success message

    **Raises:**
    - 400: Incorrect current password or weak new password
    - 401: Invalid authentication token
    """
    user_service = UserService(db)
    success, error = user_service.change_password(
        user_id=current_user_id,
        old_password=password_data.old_password,
        new_password=password_data.new_password,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return {"message": "Password changed successfully"}


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
):
    """
    Logout current user.

    Note: With JWT tokens, actual logout is handled client-side by deleting the token.
    This endpoint is provided for consistency and can be extended to support token blacklisting.

    **Returns:**
    - Success message
    """
    # In a production system, you might want to:
    # 1. Add the token to a blacklist/revocation list in Redis
    # 2. Track logout events for security monitoring
    # 3. Clear any server-side session data

    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=Token)
def refresh_token(
    current_user: User = Depends(get_current_user),
):
    """
    Refresh JWT access token.

    Requires valid authentication token. Returns a new token with extended expiration.

    **Returns:**
    - New JWT access token

    **Raises:**
    - 401: Invalid or expired authentication token
    - 403: Inactive user account
    """
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=current_user.id,
        expires_delta=access_token_expires,
        additional_claims={"role": current_user.role.value},
    )

    return Token(access_token=access_token, token_type="bearer")
