import sys
from pathlib import Path

# Add the parent directory to sys.path to resolve the import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter
from app.api.v1 import auth_endpoints as auth_module

# Import router from the auth module
auth_router = auth_module.router

from .users.routes import router as users_router
from .chat import router as chat_router
from .documents import router as documents_router
from .evaluations import router as evaluations_router
from .subjects import router as subjects_router
from .analytics import router as analytics_router

api_router = APIRouter()

api_router.include_router(auth_router)  # Already has /auth prefix
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])
api_router.include_router(evaluations_router, prefix="/evaluations", tags=["evaluations"])
api_router.include_router(subjects_router, prefix="/subjects", tags=["subjects"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
