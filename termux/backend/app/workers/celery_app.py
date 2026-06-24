import asyncio
import os
from celery import Celery
from app.core.settings import settings


celery_app = Celery(
    "app_workers",
    broker=settings.CELERY_BROKER_URL or "redis://localhost:6379/0",
    backend=settings.CELERY_RESULT_BACKEND or "redis://localhost:6379/0",
)


# Only use eager mode in development/testing — never in production
_is_testing = os.getenv("ENVIRONMENT", "development") in ("development", "test") and not settings.REDIS_URL.startswith("redis://redis")
celery_app.conf.task_always_eager = os.getenv("CELERY_TASK_ALWAYS_EAGER", "false").lower() == "true"
celery_app.conf.task_eager_propagates = celery_app.conf.task_always_eager
celery_app.conf.result_backend = settings.CELERY_RESULT_BACKEND or "redis://localhost:6379/0"




@celery_app.task(name="app.workers.process_document_task")
def process_document_task(document_id: str, tenant_id: str) -> dict:
    """Process a document: extract text, chunk, and index in vector store."""
    async def _run():
        from app.core.database import _get_session_local
        from app.services.document_service import DocumentService
        from uuid import UUID


        session_factory = _get_session_local()
        async with session_factory() as db:
            service = DocumentService(db)
            await service.process_document(UUID(document_id), UUID(tenant_id))


    asyncio.run(_run())
    return {"status": "completed", "document_id": document_id, "tenant_id": tenant_id}




@celery_app.task(name="app.workers.generate_evaluation_task")
def generate_evaluation_task(evaluation_id: str, tenant_id: str) -> dict:
    """Generate questions for an evaluation using Groq."""
    async def _run():
        from app.core.database import _get_session_local
        from app.services.evaluation_service import EvaluationService
        from uuid import UUID


        session_factory = _get_session_local()
        async with session_factory() as db:
            service = EvaluationService(db)
            await service.generate_questions(UUID(evaluation_id), UUID(tenant_id))


    asyncio.run(_run())
    return {"status": "completed", "evaluation_id": evaluation_id, "tenant_id": tenant_id}
