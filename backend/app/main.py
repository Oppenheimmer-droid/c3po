from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.core.settings import settings
from app.core.database import engine, Base
from app.api.api import api_router

# Configure logging
logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: Create tables if engine is configured
    if engine is not None:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logging.info("Database tables created successfully")
        except Exception as e:
            # Log error but don't fail startup - allow app to start for health checks
            logging.warning(f"Could not create tables: {e}")
    yield
    # Shutdown: cleanup if needed
    pass


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routes under /api
app.include_router(api_router, prefix="/api")

# Keep root endpoint for basic health check
@app.get("/")
def root():
    return {"status": "ok", "message": "C3PO backend running"}

# Railway health check endpoint (no DB required)
@app.get("/health")
def health():
    return {"status": "ok"}
