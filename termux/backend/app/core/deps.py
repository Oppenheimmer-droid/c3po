"""FastAPI dependencies for authentication, authorization, and tenant context."""

from typing import Optional, Callable
from functools import wraps
from uuid import UUID
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import verify_access_token
from app.models import User, UserRole

# HTTP Bearer token scheme
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get the current authenticated user from JWT token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = verify_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch user from database
    result = await db.execute(
        select(User).where(User.id == UUID(user_id))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Get the current user if authenticated, otherwise None."""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


class TenantContext:
    """Context holder for current tenant."""
    
    def __init__(self, tenant_id: UUID, user_id: UUID, user: Optional[User] = None):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.user = user
    
    @property
    def role(self) -> str:
        """Get the role from the user object."""
        if self.user and hasattr(self.user, 'role'):
            return self.user.role.value if hasattr(self.user.role, 'value') else str(self.user.role)
        return "student"


async def get_tenant_context(
    user: User = Depends(get_current_user),
) -> TenantContext:
    """Get tenant context from current user."""
    ctx = TenantContext(tenant_id=user.tenant_id, user_id=user.id)
    ctx.user = user
    return ctx


def require_role(*roles: UserRole):
    """Dependency factory to require specific roles."""
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in [r.value for r in roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {[r.value for r in roles]}",
            )
        return user
    return role_checker


def require_tenant():
    """Dependency to ensure request has tenant context."""
    async def tenant_checker(ctx: TenantContext = Depends(get_tenant_context)) -> TenantContext:
        if not ctx.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant context required",
            )
        return ctx
    return tenant_checker


# Role-based access decorators
def roles_required(*roles: str):
    """Decorator to enforce role requirements on route handlers."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("user")
            if not user or user.role not in roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires one of roles: {list(roles)}",
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Predefined role dependencies
require_superadmin = require_role(UserRole.SUPERADMIN)
require_admin_or_teacher = require_role(UserRole.SUPERADMIN, UserRole.ACADEMY_ADMIN, UserRole.TEACHER)
require_teacher = require_role(UserRole.TEACHER, UserRole.SUPERADMIN)
require_student = require_role(UserRole.STUDENT)


# Helper to extract tenant_id from request headers (for multi-tenant API)
async def get_tenant_id_from_header(request: Request) -> Optional[UUID]:
    """Extract tenant_id from custom header."""
    tenant_header = request.headers.get("X-Tenant-ID")
    if tenant_header:
        try:
            return UUID(tenant_header)
        except ValueError:
            return None
    return None