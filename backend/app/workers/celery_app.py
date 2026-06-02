"""Celery configuration and workers for async tasks."""

from celery import Celery
import logging

from app.core.config import settings

# Configure Celery
celery_app = Celery(
    "redrive_edu",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Logging
logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_document_task(self, document_id: str, tenant_id: str):
    """
    Async task to process a document.
    
    This task:
    1. Extracts text from the document
    2. Chunks the text
    3. Generates embeddings
    4. Stores in vector database
    """
    from app.core.database import AsyncSessionLocal
    from app.services.document_service import DocumentService
    from uuid import UUID
    import asyncio
    
    logger.info(f"Starting document processing: {document_id}")
    
    async def _process():
        async with AsyncSessionLocal() as db:
            try:
                service = DocumentService(db)
                chunk_count, vector_ids = await service.process_document(
                    document_id=UUID(document_id),
                    tenant_id=UUID(tenant_id),
                )
                logger.info(f"Document {document_id} processed: {chunk_count} chunks")
                return {"status": "success", "chunk_count": chunk_count}
            except Exception as e:
                logger.error(f"Error processing document {document_id}: {e}")
                raise self.retry(exc=e)
    
    return asyncio.run(_process())


@celery_app.task(bind=True, max_retries=3)
def delete_document_task(self, document_id: str, tenant_id: str):
    """Async task to delete a document and its vectors."""
    from app.core.database import AsyncSessionLocal
    from app.services.document_service import DocumentService
    from uuid import UUID
    import asyncio
    
    logger.info(f"Starting document deletion: {document_id}")
    
    async def _delete():
        async with AsyncSessionLocal() as db:
            try:
                service = DocumentService(db)
                success = await service.delete_document(
                    document_id=UUID(document_id),
                    tenant_id=UUID(tenant_id),
                )
                logger.info(f"Document {document_id} deleted: {success}")
                return {"status": "success", "deleted": success}
            except Exception as e:
                logger.error(f"Error deleting document {document_id}: {e}")
                raise self.retry(exc=e)
    
    return asyncio.run(_delete())


@celery_app.task(bind=True, max_retries=3)
def generate_evaluation_task(self, evaluation_id: str, tenant_id: str):
    """Async task to generate questions for an evaluation."""
    from app.core.database import AsyncSessionLocal
    from app.services.evaluation_service import EvaluationService
    from uuid import UUID
    import asyncio
    
    logger.info(f"Starting evaluation generation: {evaluation_id}")
    
    async def _generate():
        async with AsyncSessionLocal() as db:
            try:
                service = EvaluationService(db)
                result = await service.generate_questions(
                    evaluation_id=UUID(evaluation_id),
                    tenant_id=UUID(tenant_id),
                )
                logger.info(f"Evaluation {evaluation_id} generated: {result}")
                return {"status": "success", "question_count": result}
            except Exception as e:
                logger.error(f"Error generating evaluation {evaluation_id}: {e}")
                raise self.retry(exc=e)
    
    return asyncio.run(_generate())


@celery_app.task(bind=True, max_retries=3)
def grade_evaluation_task(self, attempt_id: str, tenant_id: str):
    """Async task to grade an evaluation attempt."""
    from app.core.database import AsyncSessionLocal
    from app.services.evaluation_service import EvaluationService
    from uuid import UUID
    import asyncio
    
    logger.info(f"Starting evaluation grading: {attempt_id}")
    
    async def _grade():
        async with AsyncSessionLocal() as db:
            try:
                service = EvaluationService(db)
                result = await service.grade_attempt(
                    attempt_id=UUID(attempt_id),
                    tenant_id=UUID(tenant_id),
                )
                logger.info(f"Evaluation {attempt_id} graded: score={result.get('score')}")
                return result
            except Exception as e:
                logger.error(f"Error grading evaluation {attempt_id}: {e}")
                raise self.retry(exc=e)
    
    return asyncio.run(_grade())


@celery_app.task
def cleanup_old_sessions():
    """Periodic task to clean up expired sessions."""
    from app.core.database import AsyncSessionLocal
    from datetime import datetime, timezone
    import asyncio
    
    async def _cleanup():
        async with AsyncSessionLocal() as db:
            from sqlalchemy import delete
            from app.models import UserSession, RefreshToken
            
            # Delete expired sessions
            result = await db.execute(
                delete(UserSession).where(
                    UserSession.expires_at < datetime.now(timezone.utc)
                )
            )
            await db.commit()
            logger.info(f"Cleaned up {result.rowcount} expired sessions")
    
    asyncio.run(_cleanup())