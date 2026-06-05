from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.core.settings import settings
from app.core.database import engine, Base
from app.api.api import api_router

# Configure logging for Railway visibility
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: Create tables if engine is configured
    if engine is not None and Base is not None:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.warning(f"Could not create tables: {e}")
    else:
        logger.info("Database not configured - running without persistence")
    yield
    # Shutdown
    pass


app = FastAPI(
    title=settings.APP_NAME if settings else "C3PO Backend",
    version=settings.APP_VERSION if settings else "1.0.0",
    debug=settings.DEBUG if settings else False,
    lifespan=lifespan,
)

if settings:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mount all routes under /api
app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {"status": "ok", "message": "C3PO backend running"}


@app.get("/health")
def health():
    return {"status": "ok"}
