"""
Unit tests for security utilities (password hashing, JWT tokens).
"""

import pytest
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    verify_token,
    validate_password_strength,
)


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)

        assert hashed != password
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_verify_correct_password(self):
        """Test password verification with correct password."""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_incorrect_password(self):
        """Test password verification with incorrect password."""
        password = "SecurePassword123!"
        wrong_password = "WrongPassword456!"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (salt)."""
        password = "SecurePassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestPasswordValidation:
    """Tests for password strength validation."""

    def test_valid_password(self):
        """Test validation of valid password."""
        password = "SecurePass123!"
        is_valid, error = validate_password_strength(password)

        assert is_valid is True
        assert error is None

    def test_password_too_short(self):
        """Test validation of too short password."""
        password = "Short1!"
        is_valid, error = validate_password_strength(password)

        assert is_valid is False
        assert "at least" in error.lower()

    def test_password_no_uppercase(self):
        """Test validation of password without uppercase letter."""
        password = "lowercase123!"
        is_valid, error = validate_password_strength(password)

        assert is_valid is False
        assert "uppercase" in error.lower()

    def test_password_no_lowercase(self):
        """Test validation of password without lowercase letter."""
        password = "UPPERCASE123!"
        is_valid, error = validate_password_strength(password)

        assert is_valid is False
        assert "lowercase" in error.lower()

    def test_password_no_number(self):
        """Test validation of password without number."""
        password = "NoNumbersHere!"
        is_valid, error = validate_password_strength(password)

        assert is_valid is False
        assert "number" in error.lower()


class TestJWTTokens:
    """Tests for JWT token creation and verification."""

    def test_create_token(self):
        """Test JWT token creation."""
        user_id = 123
        token = create_access_token(subject=user_id)

        assert isinstance(token, str)
        assert len(token) > 0
        assert "." in token  # JWT has parts separated by dots

    def test_verify_valid_token(self):
        """Test verification of valid JWT token."""
        user_id = 123
        token = create_access_token(subject=user_id)
        verified_id = verify_token(token)

        assert verified_id == str(user_id)

    def test_verify_invalid_token(self):
        """Test verification of invalid JWT token."""
        invalid_token = "this.is.invalid"
        verified_id = verify_token(invalid_token)

        assert verified_id is None

    def test_token_with_additional_claims(self):
        """Test creating token with additional claims."""
        user_id = 123
        claims = {"role": "admin", "organization": "pharma_corp"}
        token = create_access_token(subject=user_id, additional_claims=claims)

        # Token should be created successfully
        assert isinstance(token, str)
        verified_id = verify_token(token)
        assert verified_id == str(user_id)

    def test_different_users_different_tokens(self):
        """Test that different users get different tokens."""
        token1 = create_access_token(subject=1)
        token2 = create_access_token(subject=2)

        assert token1 != token2
        assert verify_token(token1) == "1"
        assert verify_token(token2) == "2"
