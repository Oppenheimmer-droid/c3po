"""Database configuration for both sync (Alembic) and async (FastAPI)."""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# -----------------------------
# Base declarativa compartida
# -----------------------------
Base = declarative_base()

# -----------------------------
# Engine SÍNCRONO (solo Alembic)
# -----------------------------
sync_engine = create_engine(
    settings.DATABASE_URL_SYNC,
    pool_pre_ping=True,
)

# -----------------------------
# Engine ASÍNCRONO (FastAPI)
# -----------------------------
async_engine = create_async_engine(
    settings.DATABASE_URL_ASYNC,
    pool_pre_ping=True,
)

# -----------------------------
# Session async para FastAPI
# -----------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# -----------------------------
# Dependency para FastAPI
# -----------------------------
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
