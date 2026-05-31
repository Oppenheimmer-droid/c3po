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


# -----------------------------
# AUTH: CURRENT USER
# -----------------------------
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
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

    result = await db.execute(select(User).where(User.id == UUID(user_id)))
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
    if not credentials:
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


# -----------------------------
# TENANT CONTEXT
# -----------------------------
class TenantContext:
    """Context holder for current tenant."""
    def __init__(self, tenant_id: UUID, user_id: UUID):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.user: Optional[User] = None


async def get_tenant_context(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> TenantContext:
    tenant_header = request.headers.get("X-Tenant-ID")

    if not tenant_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-Tenant-ID header"
        )

    try:
        tenant_id = UUID(tenant_header)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid X-Tenant-ID format"
        )

    ctx = TenantContext(tenant_id=tenant_id, user_id=current_user.id)
    ctx.user = current_user
    return ctx


# -----------------------------
# ROLE-BASED ACCESS CONTROL
# -----------------------------
def require_role(*allowed_roles: UserRole):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(
            *args,
            user: User = Depends(get_current_user),
            **kwargs
        ):
            if user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator


require_superadmin = require_role(UserRole.SUPERADMIN)
require_admin_or_teacher = require_role(
    UserRole.SUPERADMIN,
    UserRole.ACADEMY_ADMIN,
    UserRole.TEACHER
)
require_teacher = require_role(UserRole.TEACHER, UserRole.SUPERADMIN)
require_student = require_role(UserRole.STUDENT)
