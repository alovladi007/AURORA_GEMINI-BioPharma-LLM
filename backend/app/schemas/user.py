"""
Pydantic schemas for User model.

Request/response schemas for user-related API endpoints.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.user import UserRole


# ============================================
# Base Schemas
# ============================================

class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    role: UserRole = UserRole.RESEARCHER


# ============================================
# Request Schemas
# ============================================

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "researcher@example.com",
                "username": "john_doe",
                "full_name": "John Doe",
                "password": "SecurePassword123!",
                "role": "researcher"
            }
        }
    )


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "John Smith",
                "is_active": True
            }
        }
    )


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "john_doe",
                "password": "SecurePassword123!"
            }
        }
    )


class PasswordChange(BaseModel):
    """Schema for changing password."""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "old_password": "OldPassword123!",
                "new_password": "NewSecurePassword456!"
            }
        }
    )


# ============================================
# Response Schemas
# ============================================

class User(UserBase):
    """Schema for user response (without password)."""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserWithProjects(User):
    """Schema for user response with project count."""
    project_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# ============================================
# Authentication Schemas
# ============================================

class Token(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""
    sub: Optional[int] = None  # user_id
    exp: Optional[int] = None  # expiration time
