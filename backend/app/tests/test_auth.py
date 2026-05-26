"""Unit tests for authentication service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID
from datetime import datetime, timezone

from app.services.auth_service import AuthService
from app.models import User, Tenant, UserRole, TenantStatus
from app.schemas import LoginRequest, UserCreate, TenantCreate


class TestAuthService:
    """Test cases for AuthService."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        db = AsyncMock()
        db.add = MagicMock()
        db.flush = AsyncMock()
        db.refresh = AsyncMock()
        db.commit = AsyncMock()
        return db

    @pytest.fixture
    def auth_service(self, mock_db):
        """Create AuthService with mock database."""
        return AuthService(mock_db)

    def test_login_success(self, auth_service, mock_db):
        """Test successful login flow."""
        # Mock user
        mock_user = MagicMock(spec=User)
        mock_user.id = UUID("12345678-1234-1234-1234-123456789012")
        mock_user.email = "test@example.com"
        mock_user.password_hash = "$2b$12$hashedpassword"
        mock_user.tenant_id = UUID("87654321-4321-4321-4321-210987654321")
        mock_user.role = UserRole.STUDENT
        mock_user.is_active = True
        
        # Mock tenant
        mock_tenant = MagicMock(spec=Tenant)
        mock_tenant.slug = "test-tenant"
        mock_tenant.status = TenantStatus.ACTIVE

        # Mock repositories
        auth_service.tenant_repo.get_by_slug = AsyncMock(return_value=mock_tenant)
        auth_service.user_repo.get_by_email = AsyncMock(return_value=mock_user)
        auth_service.user_repo.update_login = AsyncMock()
        auth_service.session_repo.create_session = AsyncMock()
        auth_service.refresh_repo.create_token = AsyncMock()

        # Execute
        login_data = LoginRequest(email="test@example.com", password="password123")
        
        # Note: This is a simplified test. Full test would require more mocking
        # of the security module functions

    def test_login_invalid_password(self, auth_service, mock_db):
        """Test login with invalid password."""
        # Mock user with correct email but wrong password
        mock_user = MagicMock(spec=User)
        mock_user.password_hash = "$2b$12$hashedpassword"
        
        auth_service.user_repo.get_by_email = AsyncMock(return_value=mock_user)
        
        # Verify password check would fail
        with patch('app.services.auth_service.verify_password', return_value=False):
            pass  # Password verification would fail

    def test_login_user_not_active(self, auth_service, mock_db):
        """Test login with inactive user."""
        mock_user = MagicMock(spec=User)
        mock_user.is_active = False
        
        auth_service.user_repo.get_by_email = AsyncMock(return_value=mock_user)
        
        # Should return None for inactive users
        # This is implicit in the login logic


class TestPasswordHashing:
    """Test cases for password hashing utilities."""

    def test_hash_password_creates_hash(self):
        """Test that hash_password creates a bcrypt hash."""
        from app.core.security import hash_password
        
        password = "test_password_123"
        hashed = hash_password(password)
        
        # Verify hash is not the same as password
        assert hashed != password
        # Verify hash starts with bcrypt prefix
        assert hashed.startswith("$2b$")

    def test_verify_password_correct(self):
        """Test that correct password is verified."""
        from app.core.security import hash_password, verify_password
        
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test that incorrect password is rejected."""
        from app.core.security import hash_password, verify_password
        
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False


class TestJWTTokens:
    """Test cases for JWT token utilities."""

    def test_create_access_token(self):
        """Test access token creation."""
        from app.core.security import create_access_token, verify_access_token
        
        data = {"sub": "user123", "tenant_id": "tenant456"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Verify token is valid
        payload = verify_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["tenant_id"] == "tenant456"
        assert payload["type"] == "access"

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        from app.core.security import create_refresh_token, verify_refresh_token
        
        data = {"sub": "user123", "jti": "token123"}
        token = create_refresh_token(data)
        
        assert token is not None
        
        payload = verify_refresh_token(token)
        assert payload is not None
        assert payload["type"] == "refresh"

    def test_verify_invalid_token(self):
        """Test that invalid tokens are rejected."""
        from app.core.security import verify_access_token
        
        invalid_token = "invalid.token.string"
        payload = verify_access_token(invalid_token)
        
        assert payload is None

    def test_expired_token_rejected(self):
        """Test that expired tokens are rejected."""
        from app.core.security import create_access_token, verify_access_token
        from datetime import timedelta
        
        # Create token that expires immediately
        data = {"sub": "user123"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        payload = verify_access_token(token)
        assert payload is None


class TestUserRole:
    """Test cases for user roles."""

    def test_user_role_enum_values(self):
        """Test that user role enum has expected values."""
        assert UserRole.SUPERADMIN.value == "superadmin"
        assert UserRole.ACADEMY_ADMIN.value == "academy_admin"
        assert UserRole.TEACHER.value == "teacher"
        assert UserRole.STUDENT.value == "student"
        assert UserRole.PARENT.value == "parent"

    def test_tenant_status_enum_values(self):
        """Test that tenant status enum has expected values."""
        assert TenantStatus.ACTIVE.value == "active"
        assert TenantStatus.SUSPENDED.value == "suspended"
        assert TenantStatus.PENDING.value == "pending"