from pydantic import BaseModel
from fastapi import Header, HTTPException
from typing import Optional

class TenantContext(BaseModel):
    tenant_id: str = "dummy-tenant"
    user_id: str = "dummy-user"
    role: str = "student"


async def get_tenant_context(
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
    x_tenant_slug: Optional[str] = Header(None, alias="X-Tenant-Slug"),
    authorization: Optional[str] = Header(None),
) -> TenantContext:
    """Get tenant context from request headers.
    
    In production, this should extract and validate JWT token
    to get the actual tenant_id, user_id, and role.
    """
    # For development, return dummy context
    # In production, decode JWT and extract claims
    return TenantContext(
        tenant_id=x_tenant_id or "dummy-tenant",
        user_id="dummy-user",
        role="student",
    )
