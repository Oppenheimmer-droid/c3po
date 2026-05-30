from sqlalchemy import select
from app.models.user import User

class UserRepository:
    def __init__(self, db):
        self.db = db

    async def get_default_user_for_tenant(self, tenant_id):
        """
        Devuelve el usuario principal del tenant.
        Si hay varios, devuelve el primero con rol admin.
        """
        stmt = select(User).where(User.tenant_id == tenant_id)

        result = await self.db.execute(stmt)
        users = result.scalars().all()

        if not users:
            return None

        # Prioridad: superadmin → academy_admin → teacher → student
        role_priority = ["superadmin", "academy_admin", "teacher", "student"]

        users_sorted = sorted(
            users,
            key=lambda u: role_priority.index(u.role.value)
        )

        return users_sorted[0]

    async def get_by_tenant_and_user_id(self, tenant_id, user_id):
        """
        Método original, por si lo necesitas.
        """
        stmt = select(User).where(
            User.id == user_id,
            User.tenant_id == tenant_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

