"""C3PO Backend - FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import re

# Simple working CORS check
def is_vercel_origin(origin: str) -> bool:
    """Check if origin is a Vercel domain."""
    if not origin:
        return False
    # Match any vercel.app domain
    pattern = r'^https://[a-zA-Z0-9-]+\.vercel\.app$'
    return bool(re.match(pattern, origin))

app = FastAPI(title="C3PO Backend", version="1.0.0")

# CORS middleware with wildcard support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "message": "C3PO backend running"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# Auth endpoints placeholder (import from actual module)
try:
    from app.api.api import api_router
    app.include_router(api_router, prefix="/api")
except Exception as e:
    print(f"Warning: Could not load API router: {e}")
