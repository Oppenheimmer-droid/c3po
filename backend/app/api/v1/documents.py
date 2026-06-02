"""Document API endpoints."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user, get_tenant_context, TenantContext, require_admin_or_teacher
from app.services.document_service import DocumentService
from app.schemas import (
    DocumentResponse, DocumentListResponse, DocumentMetadata,
    DocumentChunkResponse,
)
from app.workers.celery_app import process_document_task

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    subject_id: Optional[UUID] = Form(None),
    topic_id: Optional[UUID] = Form(None),
    difficulty: int = Form(1, ge=1, le=5),
    tags: Optional[str] = Form(None),  # Comma-separated
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Upload a new document for processing."""
    # Validate file type
    allowed_extensions = [".pdf", ".docx", ".txt", ".md"]
    ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(allowed_extensions)}",
        )
    
    # Read file content
    content = await file.read()
    
    # Check file size (50MB default)
    from app.core.config import settings
    if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB",
        )
    
    # Parse tags
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
    
    # Create document
    service = DocumentService(db)
    document = await service.create_document(
        tenant_id=ctx.tenant_id,
        user_id=ctx.user_id,
        filename=file.filename,
        file_content=content,
        title=title,
        description=description,
        subject_id=subject_id,
        topic_id=topic_id,
        difficulty=difficulty,
        tags=tag_list,
    )
    
    # Queue processing task
    process_document_task.delay(str(document.id), str(ctx.tenant_id))
    
    return document


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    subject_id: Optional[UUID] = Query(None),
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """List all documents for the tenant."""
    skip = (page - 1) * page_size
    
    service = DocumentService(db)
    documents, total = await service.list_documents(
        tenant_id=ctx.tenant_id,
        skip=skip,
        limit=page_size,
        status=status_filter,
    )
    
    pages = (total + page_size - 1) // page_size
    
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(d) for d in documents],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific document by ID."""
    service = DocumentService(db)
    document = await service.get_document(document_id, ctx.tenant_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Delete a document and its associated data."""
    # Only admins and teachers can delete
    if ctx.user.role.value not in ["superadmin", "academy_admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and teachers can delete documents",
        )
    
    service = DocumentService(db)
    success = await service.delete_document(document_id, ctx.tenant_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    return None


@router.get("/{document_id}/chunks", response_model=list[DocumentChunkResponse])
async def get_document_chunks(
    document_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get document chunks for preview."""
    from app.repositories.documents import DocumentChunkRepository
    
    # Verify document belongs to tenant
    service = DocumentService(db)
    document = await service.get_document(document_id, ctx.tenant_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    chunk_repo = DocumentChunkRepository(db)
    chunks = await chunk_repo.get_by_document(document_id, skip, limit)
    
    return [DocumentChunkResponse.model_validate(c) for c in chunks]


@router.post("/{document_id}/reprocess", status_code=status.HTTP_202_ACCEPTED)
async def reprocess_document(
    document_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Re-process a document (e.g., after fixing issues)."""
    # Only admins and teachers can reprocess
    if ctx.user.role.value not in ["superadmin", "academy_admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and teachers can reprocess documents",
        )
    
    service = DocumentService(db)
    document = await service.get_document(document_id, ctx.tenant_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    # Reset status and queue for reprocessing
    document.status = "pending"
    await db.flush()
    
    process_document_task.delay(str(document_id), str(ctx.tenant_id))
    
    return {"message": "Document queued for reprocessing"}