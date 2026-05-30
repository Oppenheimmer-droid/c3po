from fastapi import Header
from pydantic import BaseModel

class TenantContext(BaseModel):
    tenant_id: str

async def get_tenant_context(x_tenant_id: str = Header(...)):
    return TenantContext(tenant_id=x_tenant_id)
