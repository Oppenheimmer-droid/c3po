"""Authentication service with JWT, registration, and session management."""

from typing import Optional, Tuple
from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, UserRole, Tenant, TenantStatus
from app.repositories.auth import UserRepository, TenantRepository, SessionRepository, RefreshTokenRepository
from app.core.security import (
    verify_password, hash_password, 
    create_access_token, create_refresh_token, verify_refresh_token
)
from app.schemas import (
    LoginRequest, TokenResponse, UserCreate, UserResponse,
    TenantCreate, TenantResponse
)
from app.core.config import settings


class AuthService:
    """Authentication and user management service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.tenant_repo = TenantRepository(db)
        self.session_repo = SessionRepository(db)
        self.refresh_repo = RefreshTokenRepository(db)
    
    async def register_tenant_and_user(
        self,
        tenant_data: TenantCreate,
        user_data: UserCreate,
    ) -> Tuple[Tenant, User]:
        """Register a new tenant and its first admin user."""
        # Create tenant
        tenant = Tenant(
            name=tenant_data.name,
            slug=tenant_data.slug,
            status=TenantStatus.ACTIVE,
        )
        self.db.add(tenant)
        await self.db.flush()
        
        # Create admin user for the tenant
        user = await self.user_repo.create_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            tenant_id=tenant.id,
            role=UserRole.ACADEMY_ADMIN,
        )
        
        return tenant, user
    
    async def login(
        self,
        login_data: LoginRequest,
        tenant_slug: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> Optional[TokenResponse]:
        """Authenticate user and return tokens."""
        # Get tenant
        tenant = await self.tenant_repo.get_by_slug(tenant_slug)
        if not tenant or tenant.status != TenantStatus.ACTIVE:
            return None
        
        # Get user
        user = await self.user_repo.get_by_email(login_data.email, tenant.id)
        if not user or not verify_password(login_data.password, user.password_hash):
            return None
        
        if not user.is_active:
            return None
        
        # Update last login
        await self.user_repo.update_login(user.id)
        
        # Create tokens
        token_id = f"at-{user.id}-{datetime.now(timezone.utc).timestamp()}"
        access_token = create_access_token(
            data={"sub": str(user.id), "tenant_id": str(user.tenant_id), "role": user.role.value}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "jti": token_id}
        )
        
        # Store session and refresh token
        await self.session_repo.create_session(
            user_id=user.id,
            token_id=token_id,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        
        await self.refresh_repo.create_token(
            user_id=user.id,
            token_hash=hash_password(refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        
        await self.db.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[TokenResponse]:
        """Refresh access token using refresh token."""
        payload = verify_refresh_token(refresh_token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        jti = payload.get("jti")
        
        if not user_id:
            return None
        
        # Verify refresh token in database
        token_hash = hash_password(refresh_token)
        stored_token = await self.refresh_repo.get_token(token_hash)
        if not stored_token or stored_token.user_id != UUID(user_id):
            return None
        
        # Get user
        user = await self.user_repo.get_by_id(UUID(user_id))
        if not user or not user.is_active:
            return None
        
        # Create new access token
        access_token = create_access_token(
            data={"sub": str(user.id), "tenant_id": str(user.tenant_id), "role": user.role.value}
        )
        
        # Create new refresh token (token rotation)
        new_refresh_token = create_refresh_token(
            data={"sub": str(user.id), "jti": f"rt-{user.id}-{datetime.now(timezone.utc).timestamp()}"}
        )
        
        # Revoke old refresh token and create new one
        await self.refresh_repo.revoke_token(token_hash)
        await self.refresh_repo.create_token(
            user_id=user.id,
            token_hash=hash_password(new_refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        
        await self.db.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    
    async def logout(self, user_id: UUID) -> None:
        """Logout user by revoking all tokens and sessions."""
        await self.session_repo.delete_user_sessions(user_id)
        await self.refresh_repo.revoke_user_tokens(user_id)
        await self.db.commit()
    
    async def change_password(
        self, user_id: UUID, current_password: str, new_password: str
    ) -> bool:
        """Change user password."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return False
        
        if not verify_password(current_password, user.password_hash):
            return False
        
        user.password_hash = hash_password(new_password)
        await self.db.flush()
        
        # Revoke all tokens and sessions
        await self.session_repo.delete_user_sessions(user_id)
        await self.refresh_repo.revoke_user_tokens(user_id)
        
        await self.db.commit()
        return True
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        return await self.user_repo.get_by_id(user_id)
    
    async def get_tenant_users(
        self, tenant_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """Get all users for a tenant."""
        return await self.user_repo.get_by_tenant(tenant_id, skip, limit)