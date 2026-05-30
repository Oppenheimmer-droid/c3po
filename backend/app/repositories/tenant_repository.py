from sqlalchemy import select
from app.models.auth import Tenant

class TenantRepository:
    def __init__(self, db):
        self.db = db

    async def get_by_api_key(self, api_key: str):
        stmt = select(Tenant).where(Tenant.api_key == api_key)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
