from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.core.security import verify_access_token
from backend.app.models import User

class TenantContext:
    def __init__(self, tenant_id: UUID, user_id: UUID):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.user: Optional[User] = None

async def get_tenant_context(
    request: Request,
    current_user: User = Depends(),
    db: AsyncSession = Depends(get_db),
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
