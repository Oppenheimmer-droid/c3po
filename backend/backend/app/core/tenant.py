from pydantic import BaseModel

class TenantContext(BaseModel):
    tenant_id: str = "dummy-tenant"
    user_id: str = "dummy-user"
    role: str = "student"

async def get_tenant_context():
    return TenantContext()
