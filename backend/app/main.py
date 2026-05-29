from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import settings
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,   # IMPORTANTE
    allow_methods=["*"],
    allow_headers=["*"],
)

# CORS
    

# Routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Healthcheck
@app.get("/")
def root():
    return {"status": "ok"}
