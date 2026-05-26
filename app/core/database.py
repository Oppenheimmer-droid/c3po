from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Base de modelos
Base = declarative_base()

# URL async (para FastAPI)
DATABASE_URL_ASYNC = settings.DATABASE_URL_ASYNC

# URL sync (para Alembic)
DATABASE_URL_SYNC = settings.DATABASE_URL_SYNC

# Motor async para la app
async_engine = create_async_engine(
    DATABASE_URL_ASYNC,
    echo=False,
    future=True,
)

# Session async
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Dependency para FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
