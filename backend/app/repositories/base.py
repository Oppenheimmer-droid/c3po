"""Base repository with common CRUD operations."""

from typing import Optional, TypeVar, Generic, Type
from uuid import UUID
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Base repository with common database operations."""
    
    def __init__(self, model: Type[T], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Get a single record by ID."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_ids(self, ids: list[UUID]) -> list[T]:
        """Get multiple records by IDs."""
        result = await self.db.execute(
            select(self.model).where(self.model.id.in_(ids))
        )
        return list(result.scalars().all())
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        """Get all records with pagination."""
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def count(self) -> int:
        """Count total records."""
        result = await self.db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar() or 0
    
    async def create(self, obj: T) -> T:
        """Create a new record."""
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj
    
    async def update(self, id: UUID, data: dict) -> Optional[T]:
        """Update a record by ID."""
        await self.db.execute(
            update(self.model).where(self.model.id == id).values(**data)
        )
        await self.db.flush()
        return await self.get_by_id(id)
    
    async def delete(self, id: UUID) -> bool:
        """Delete a record by ID."""
        result = await self.db.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.db.flush()
        return result.rowcount > 0
    
    async def exists(self, id: UUID) -> bool:
        """Check if a record exists."""
        result = await self.db.execute(
            select(func.count()).select_from(self.model).where(self.model.id == id)
        )
        return (result.scalar() or 0) > 0