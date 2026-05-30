from app.core.tenant import TenantContext, get_tenant_context
from fastapi import APIRouter

from .auth.routes import router as auth_router
from .users.routes import router as users_router
from .chat import router as chat_router
from .documents import router as documents_router
from .evaluations import router as evaluations_router
from .subjects import router as subjects_router
from .analytics import router as analytics_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])
api_router.include_router(evaluations_router, prefix="/evaluations", tags=["evaluations"])
api_router.include_router(subjects_router, prefix="/subjects", tags=["subjects"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
