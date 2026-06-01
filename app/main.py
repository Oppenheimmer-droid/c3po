from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.api.roles import router as roles_router
from app.api.auth import router as auth_router
from app.services.rag_pipeline import answer_with_role
from app.core.roles import ROLES
from pydantic import BaseModel
import os

app = FastAPI(
    title="C3PO - AI Tutor Platform",
    version="1.0.0",
    debug=os.getenv("DEBUG", "false").lower() == "true"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(roles_router, prefix="/api/v1/roles", tags=["roles"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])

# Healthcheck endpoints
@app.get("/")
def root():
    return {"status": "ok", "service": "C3PO Backend", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ui")
def ui():
    """Serve the frontend UI."""
    return FileResponse("index.html", media_type="text/html")

# RAG Query endpoint
class QueryRequest(BaseModel):
    query: str
    role: str = "matematicas"

@app.post("/api/v1/query")
def query(req: QueryRequest):
    """Execute a RAG query with the specified role."""
    return answer_with_role(req.query, req.role)

# List available roles
@app.get("/api/v1/roles")
def list_roles():
    """List all available tutoring roles."""
    return {
        "roles": [
            {
                "id": role_id,
                "name": data["name"],
                "style": data["style"],
                "tone": data["tone"]
            }
            for role_id, data in ROLES.items()
        ]
    }
