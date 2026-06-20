import asyncio
from celery import Celery
from app.core.settings import settings

# Create a local Celery app with eager execution for development/testing.
# In production with Redis, set task_always_eager = False and deploy a worker.
celery_app = Celery(
    "app_workers",
    broker=settings.CELERY_BROKER_URL or "redis://localhost:6379/0",
    backend=settings.CELERY_RESULT_BACKEND or "redis://localhost:6379/0",
)
celery_app.conf.task_always_eager = True
celery_app.conf.result_backend = settings.CELERY_RESULT_BACKEND or "redis://localhost:6379/0"
celery_app.conf.task_eager_propagates = True


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
