from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import settings
from app.api.v1.router import api_router
import app.lazy_imports as lazy

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {"status": "ok", "routers": "loaded"}
