from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from contextlib import asynccontextmanager
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import settings
try:
    from app.core.settings import settings
except Exception as e:
    logger.warning(f"Could not import settings: {e}")
    settings = None

# Import database
try:
    from app.core.database import engine, Base
except Exception as e:
    logger.warning(f"Could not import database: {e}")
    engine = None
    Base = None


def is_origin_allowed(origin: str, allowed_origins: list) -> bool:
    """Check if origin matches any allowed pattern (including wildcards)."""
    for pattern in allowed_origins:
        if pattern == "*":
            return True
        if pattern == origin:
            return True
        # Handle wildcard patterns like https://*.vercel.app
        if pattern.startswith("https://") and ".vercel.app" in pattern:
            regex_pattern = pattern.replace(".", "\\.").replace("*", ".*")
            if re.match(f"^{regex_pattern}$", origin):
                return True
        # Handle http://localhost:3000 style
        if pattern.startswith("http://localhost:"):
            if origin.startswith("http://localhost:"):
                return True
    return False


class FlexibleCORSMiddleware(BaseHTTPMiddleware):
    """Custom CORS middleware that supports wildcard domains."""
    
    def __init__(self, app, allowed_origins: list, allow_credentials: bool = True):
        super().__init__(app)
        self.allowed_origins = allowed_origins
        self.allow_credentials = allow_credentials
        
    async def dispatch(self, request: Request, call_next):
        # Handle preflight OPTIONS requests
        if request.method == "OPTIONS":
            origin = request.headers.get("origin", "")
            
            # Check if origin is allowed
            if is_origin_allowed(origin, self.allowed_origins) or "*" in self.allowed_origins:
                response = JSONResponse(content="", status_code=200)
                response.headers["Access-Control-Allow-Origin"] = origin if origin else "*"
                response.headers["Access-Control-Allow-Methods"] = "*"
                response.headers["Access-Control-Allow-Headers"] = "*"
                response.headers["Access-Control-Allow-Credentials"] = "true" if self.allow_credentials else "false"
                response.headers["Access-Control-Max-Age"] = "3600"
                return response
            else:
                return JSONResponse(
                    content={"detail": "CORS origin not allowed"},
                    status_code=403
                )
        
        # Process regular requests
        response = await call_next(request)
        
        origin = request.headers.get("origin", "")
        if is_origin_allowed(origin, self.allowed_origins) or "*" in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin if origin else "*"
            if self.allow_credentials:
                response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Expose-Headers"] = "*"
            
        return response


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
    pass


# Base CORS origins
cors_origins = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "http://frontend:3000",
    "https://*.vercel.app",
]

# Add settings CORS origins if available
if settings and hasattr(settings, 'CORS_ORIGINS'):
    for origin in settings.CORS_ORIGINS:
        if origin not in cors_origins:
            cors_origins.append(origin)

app = FastAPI(
    title=settings.APP_NAME if settings and hasattr(settings, 'APP_NAME') else "C3PO Backend",
    version=settings.APP_VERSION if settings and hasattr(settings, 'APP_VERSION') else "1.0.0",
    lifespan=lifespan,
)

# Add custom flexible CORS middleware
app.add_middleware(FlexibleCORSMiddleware, allowed_origins=cors_origins, allow_credentials=True)

# Mount API routes
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
