"""User and tenant repositories."""

from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, update, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Tenant, UserSession, RefreshToken, UserRole
from app.repositories.base import BaseRepository
from app.core.security import hash_password


class UserRepository(BaseRepository[User]):
    """Repository for User operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_email(self, email: str, tenant_id: UUID) -> Optional[User]:
        """Get user by email within a tenant."""
        result = await self.db.execute(
            select(User).where(
                and_(User.email == email, User.tenant_id == tenant_id)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_email_global(self, email: str) -> Optional[User]:
        """Get user by email across all tenants (for superadmin operations)."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_tenant(
        self, tenant_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """Get all users for a tenant."""
        result = await self.db.execute(
            select(User)
            .where(User.tenant_id == tenant_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def count_by_tenant(self, tenant_id: UUID) -> int:
        """Count users in a tenant."""
        result = await self.db.execute(
            select(func.count()).select_from(User).where(User.tenant_id == tenant_id)
        )
        return result.scalar() or 0
    
    async def create_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        tenant_id: UUID,
        role: UserRole = UserRole.STUDENT,
    ) -> User:
        """Create a new user with hashed password."""
        user = User(
            email=email,
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            tenant_id=tenant_id,
            role=role,
        )
        return await self.create(user)
    
    async def update_login(self, user_id: UUID) -> None:
        """Update last login timestamp."""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login=datetime.now(timezone.utc))
        )
        await self.db.flush()


class TenantRepository(BaseRepository[Tenant]):
    """Repository for Tenant operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Tenant, db)
    
    async def get_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        result = await self.db.execute(
            select(Tenant).where(Tenant.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def get_active_tenants(self, skip: int = 0, limit: int = 100) -> list[Tenant]:
        """Get all active tenants."""
        result = await self.db.execute(
            select(Tenant)
            .where(Tenant.status == "active")
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


class SessionRepository:
    """Repository for session management."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_session(
        self,
        user_id: UUID,
        token_id: str,
        expires_at: datetime,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> UserSession:
        """Create a new user session."""
        session = UserSession(
            user_id=user_id,
            token_id=token_id,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at,
        )
        self.db.add(session)
        await self.db.flush()
        return session
    
    async def get_session(self, token_id: str) -> Optional[UserSession]:
        """Get session by token ID."""
        result = await self.db.execute(
            select(UserSession).where(UserSession.token_id == token_id)
        )
        return result.scalar_one_or_none()
    
    async def delete_session(self, token_id: str) -> bool:
        """Delete a session."""
        result = await self.db.execute(
            delete(UserSession).where(UserSession.token_id == token_id)
        )
        await self.db.flush()
        return result.rowcount > 0
    
    async def delete_user_sessions(self, user_id: UUID) -> int:
        """Delete all sessions for a user."""
        result = await self.db.execute(
            delete(UserSession).where(UserSession.user_id == user_id)
        )
        await self.db.flush()
        return result.rowcount


class RefreshTokenRepository:
    """Repository for refresh token management."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_token(
        self,
        user_id: UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        """Create a new refresh token."""
        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.db.add(token)
        await self.db.flush()
        return token
    
    async def get_token(self, token_hash: str) -> Optional[RefreshToken]:
        """Get refresh token by hash."""
        result = await self.db.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.token_hash == token_hash,
                    RefreshToken.is_revoked == False,
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def revoke_token(self, token_hash: str) -> bool:
        """Revoke a refresh token."""
        result = await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .values(is_revoked=True)
        )
        await self.db.flush()
        return result.rowcount > 0
    
    async def revoke_user_tokens(self, user_id: UUID) -> int:
        """Revoke all tokens for a user."""
        result = await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .values(is_revoked=True)
        )
        await self.db.flush()
        return result.rowcount