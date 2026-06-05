from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

# Configure logging for Railway visibility
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import settings, handle gracefully
try:
    from app.core.settings import settings
except Exception as e:
    logger.warning(f"Could not import settings: {e}")
    settings = None

# Try to import database
try:
    from app.core.database import engine, Base
except Exception as e:
    logger.warning(f"Could not import database: {e}")
    engine = None
    Base = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    if engine is not None and Base is not None:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.warning(f"Could not create tables: {e}")
    yield
    # Shutdown
    pass


app = FastAPI(
    title=settings.APP_NAME if settings and hasattr(settings, 'APP_NAME') else "C3PO Backend",
    version=settings.APP_VERSION if settings and hasattr(settings, 'APP_VERSION') else "1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
cors_origins = ["http://localhost:3000", "http://localhost:3001", "http://frontend:3000"]
if settings and hasattr(settings, 'CORS_ORIGINS'):
    cors_origins.extend(settings.CORS_ORIGINS)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routes under /api
try:
    from app.api.api import api_router
    app.include_router(api_router, prefix="/api")
except Exception as e:
    logger.warning(f"Could not mount API router: {e}")


@app.get("/")
def root():
    return {"status": "ok", "message": "C3PO backend running"}


@app.get("/health")
def health():
    return {"status": "ok"}
