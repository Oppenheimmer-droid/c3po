from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.settings import settings
from app.core.database import is_database_configured
from app.api.v1.health import router as health_router
from app.api.v1.router import api_router

app = FastAPI(
    title="C3PO API",
    version="1.0.2",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None,
)

# ── CORS — debe ir antes de los routers ──────────────────────
# Allow all origins for production flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Tenant-ID", "X-Tenant-Slug", "X-Requested-With"],
    expose_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────
app.include_router(health_router, prefix="/api/v1")
app.include_router(api_router,    prefix="/api/v1")


@app.get("/")
def root():
    db_configured = is_database_configured()
    return {
        "message": "C3PO API running",
        "environment": settings.ENVIRONMENT,
        "database_configured": db_configured,
    }


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request, exc):
    """Handle runtime errors like missing DATABASE_URL."""
    return JSONResponse(
        status_code=503,
        content={
            "detail": str(exc),
            "type": "configuration_error",
        }
    )
