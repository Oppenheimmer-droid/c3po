from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.settings import settings

# Forzar asyncpg aunque DATABASE_URL venga sin el driver
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

async_engine = create_async_engine(db_url, echo=False)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
