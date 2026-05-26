"""Subject API endpoints."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, TenantContext, require_admin_or_teacher
from app.repositories.documents import SubjectRepository, TopicRepository
from app.schemas import (
    TenantResponse,
)

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("", response_model=List[dict])
async def list_subjects(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """List all subjects for the tenant."""
    repo = SubjectRepository(db)
    subjects = await repo.get_by_tenant(ctx.tenant_id)
    
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "code": s.code,
            "description": s.description,
        }
        for s in subjects
    ]


@router.get("/{subject_id}/topics", response_model=List[dict])
async def list_subject_topics(
    subject_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """List all topics for a subject."""
    topic_repo = TopicRepository(db)
    topics = await topic_repo.get_by_subject(subject_id)
    
    return [
        {
            "id": str(t.id),
            "name": t.name,
            "description": t.description,
            "difficulty": t.difficulty,
        }
        for t in topics
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_subject(
    name: str,
    code: str,
    description: Optional[str] = None,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Create a new subject (admin/teacher only)."""
    if ctx.user.role.value not in ["superadmin", "academy_admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and teachers can create subjects",
        )
    
    repo = SubjectRepository(db)
    
    # Check if code already exists
    existing = await repo.get_by_code(ctx.tenant_id, code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subject code already exists",
        )
    
    from app.models import Subject
    subject = Subject(
        tenant_id=ctx.tenant_id,
        name=name,
        code=code,
        description=description,
    )
    
    db.add(subject)
    await db.flush()
    await db.refresh(subject)
    
    return {"id": str(subject.id), "name": subject.name, "code": subject.code}


@router.post("/{subject_id}/topics", status_code=status.HTTP_201_CREATED)
async def create_topic(
    subject_id: UUID,
    name: str,
    description: Optional[str] = None,
    difficulty: int = Query(1, ge=1, le=5),
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Create a new topic within a subject."""
    if ctx.user.role.value not in ["superadmin", "academy_admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and teachers can create topics",
        )
    
    from app.models import Topic
    topic = Topic(
        subject_id=subject_id,
        name=name,
        description=description,
        difficulty=difficulty,
    )
    
    db.add(topic)
    await db.flush()
    await db.refresh(topic)
    
    return {"id": str(topic.id), "name": topic.name, "difficulty": topic.difficulty}