from fastapi import Header, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.tenant_repository import TenantRepository

class TenantContext(BaseModel):
    tenant_id: str
    user_id: str
    user: dict
    api_key: str

async def get_tenant_context(
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> TenantContext:

    tenant_repo = TenantRepository(db)
    tenant = await tenant_repo.get_by_api_key(x_api_key)

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    # Usuario virtual = tenant
    virtual_user_id = str(tenant.id)

    return TenantContext(
        tenant_id=str(tenant.id),
        user_id=virtual_user_id,
        user={"id": virtual_user_id, "role": "academy_admin"},
        api_key=x_api_key
    )
