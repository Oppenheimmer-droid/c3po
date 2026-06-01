from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.core.config import settings
from app.core.base import Base

# Determinar URLs
DATABASE_URL_ASYNC = getattr(settings, "DATABASE_URL", None)
DATABASE_URL_SYNC = getattr(settings, "DATABASE_URL_SYNC", None)

# Crear engine asíncrono para sqlite (aiosqlite) o postgresql (asyncpg)
async_engine = None
AsyncSessionLocal = None

if DATABASE_URL_ASYNC:
    async_driver = None
    if "asyncpg" in DATABASE_URL_ASYNC or "postgresql" in DATABASE_URL_ASYNC:
        async_driver = "asyncpg"
    elif "aiosqlite" in DATABASE_URL_ASYNC or "sqlite" in DATABASE_URL_ASYNC:
        async_driver = "aiosqlite"
    
    if async_driver:
        async_engine = create_async_engine(
            DATABASE_URL_ASYNC,
            future=True,
            echo=False,
        )

        AsyncSessionLocal = async_sessionmaker(
            bind=async_engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if AsyncSessionLocal is None:
        raise RuntimeError("Async database not configured. Ensure DATABASE_URL uses an async driver like asyncpg or aiosqlite.")

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
