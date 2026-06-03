"""Authentication API endpoints."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user, TenantContext, get_tenant_context
from app.services.auth_service import AuthService
from app.schemas import (
    LoginRequest, TokenResponse, RefreshRequest,
    UserCreate, UserResponse, UserMeResponse,
    TenantCreate, TenantResponse,
    ChangePasswordRequest, ErrorResponse,
)
from app.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def register_tenant_and_admin(
    tenant_data: TenantCreate,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new tenant with an admin user."""
    service = AuthService(db)
    
    try:
        tenant, user = await service.register_tenant_and_user(tenant_data, user_data)
        return tenant
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Login with email and password. Tenant is determined from headers or default."""
    service = AuthService(db)
    
    tenant_slug = request.headers.get("X-Tenant-Slug")
    tenant_id_header = request.headers.get("X-Tenant-ID")
    tenant_id = None
    if tenant_id_header:
        try:
            tenant_id = UUID(tenant_id_header)
        except ValueError:
            tenant_id = None
    
    user_agent = request.headers.get("User-Agent")
    ip_address = request.client.host if request.client else None
    
    result = await service.login(
        login_data=login_data,
        tenant_slug=tenant_slug,
        tenant_id=tenant_id,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    return result


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using refresh token."""
    service = AuthService(db)
    
    result = await service.refresh_access_token(refresh_data.refresh_token)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    return result


@router.post("/logout")
async def logout(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Logout current user."""
    service = AuthService(db)
    await service.logout(ctx.user_id)
    return {"message": "Logged out successfully"}


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Change password for current user."""
    service = AuthService(db)
    
    success = await service.change_password(
        user_id=ctx.user_id,
        current_password=password_data.current_password,
        new_password=password_data.new_password,
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    
    return {"message": "Password changed successfully"}


@router.get("/me", response_model=UserMeResponse)
async def get_current_user_info(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get current user information."""
    if not ctx.user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserMeResponse(
        id=ctx.user.id,
        email=ctx.user.email,
        first_name=ctx.user.first_name,
        last_name=ctx.user.last_name,
        role=ctx.user.role.value,
        tenant_id=ctx.user.tenant_id,
        tenant_name="",  # Will be populated from tenant
    )


@router.get("/users", response_model=list[UserResponse])
async def list_tenant_users(
    skip: int = 0,
    limit: int = 100,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """List all users in the current tenant."""
    # Only admins can list users
    if ctx.user.role.value not in ["superadmin", "academy_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can list users",
        )
    
    service = AuthService(db)
    users = await service.get_tenant_users(ctx.tenant_id, skip, limit)
    return users