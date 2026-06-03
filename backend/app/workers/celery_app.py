from celery import Celery
from app.core.config import settings

# Create a local Celery app with eager execution for development/testing.
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
    """Placeholder task for document processing."""
    return {"document_id": document_id, "tenant_id": tenant_id}


@celery_app.task(name="app.workers.generate_evaluation_task")
def generate_evaluation_task(evaluation_id: str, tenant_id: str) -> dict:
    """Placeholder task for evaluation generation."""
    return {"evaluation_id": evaluation_id, "tenant_id": tenant_id}
