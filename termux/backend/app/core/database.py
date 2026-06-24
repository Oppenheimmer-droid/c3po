from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from app.core.base import Base

# Engine y sessionmaker se crean lazy (primera petición real)
# para evitar crashes en build-time cuando DATABASE_URL está vacía.
_async_engine: Optional[AsyncEngine] = None
_AsyncSessionLocal: Optional[async_sessionmaker] = None


def _normalize_db_url(url: str) -> str:
    """
    Garantiza que la URL use el driver asyncpg explícitamente.

    Railway entrega:  postgresql://...   o  postgresql+asyncpg://...
    SQLAlchemy >=2.x con "postgresql://" intenta usar psycopg v3 → crash.
    Este helper lo normaliza siempre a "postgresql+asyncpg://".
    """
    if not url:
        return url
    # Sustituir cualquier variante de driver por asyncpg
    for prefix in (
        "postgresql+psycopg://",
        "postgresql+psycopg2://",
        "postgresql+psycopg3://",
        "postgres://",          # Heroku/Railway legacy
        "postgresql://",        # URL sin driver explícito
    ):
        if url.startswith(prefix):
            return "postgresql+asyncpg://" + url[len(prefix):]
    return url


def is_database_configured() -> bool:
    """Check if database is properly configured."""
    from app.core.settings import settings
    return bool(settings.DATABASE_URL)


def _get_engine() -> AsyncEngine:
    global _async_engine
    if _async_engine is None:
        from app.core.settings import settings
        raw_url = settings.DATABASE_URL
        if not raw_url:
            raise RuntimeError(
                "DATABASE_URL no está configurada. "
                "Añádela en Railway → Variables."
            )
        db_url = _normalize_db_url(raw_url)
        _async_engine = create_async_engine(
            db_url,
            future=True,
            echo=False,
            pool_pre_ping=True,          # detecta conexiones muertas
            pool_size=5,
            max_overflow=10,
        )
    return _async_engine


def _get_session_local() -> async_sessionmaker:
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = async_sessionmaker(
            bind=_get_engine(),
            expire_on_commit=False,
            class_=AsyncSession,
        )
    return _AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependencia FastAPI — inyecta una sesión de BD por request."""
    session_factory = _get_session_local()
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
