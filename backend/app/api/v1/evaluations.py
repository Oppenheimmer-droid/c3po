"""Evaluation API endpoints."""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, TenantContext, require_admin_or_teacher
from app.services.evaluation_service import EvaluationService
from app.models import Evaluation, Question, EvaluationAttempt
from app.schemas import (
    EvaluationCreate, EvaluationResponse, QuestionResponse,
    EvaluationAttemptStart, EvaluationAttemptSubmit, EvaluationAttemptResponse,
)
from app.repositories import DocumentRepository

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@router.post("", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED)
async def create_evaluation(
    eval_data: EvaluationCreate,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Create a new evaluation from a document."""
    # Only admins and teachers can create evaluations
    if ctx.user.role.value not in ["superadmin", "academy_admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and teachers can create evaluations",
        )
    
    service = EvaluationService(db)
    
    try:
        evaluation = await service.generate_evaluation(
            tenant_id=ctx.tenant_id,
            document_id=eval_data.document_id,
            created_by=ctx.user_id,
            title=eval_data.title,
            description=eval_data.description,
            question_count=eval_data.question_count,
            difficulty=eval_data.difficulty,
            evaluation_type=eval_data.evaluation_type,
            time_limit_minutes=eval_data.time_limit_minutes,
            passing_score=eval_data.passing_score,
        )
        
        # Queue question generation
        generate_evaluation_task.delay(str(evaluation.id), str(ctx.tenant_id))
        
        return evaluation
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("", response_model=List[EvaluationResponse])
async def list_evaluations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    document_id: Optional[UUID] = Query(None),
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """List evaluations for the tenant."""
    from sqlalchemy import select, func
    
    query = select(Evaluation).where(Evaluation.tenant_id == ctx.tenant_id)
    
    if document_id:
        query = query.where(Evaluation.document_id == document_id)
    
    offset = (page - 1) * page_size
    result = await db.execute(
        query.order_by(Evaluation.created_at.desc()).offset(offset).limit(page_size)
    )
    evaluations = list(result.scalars().all())
    
    return evaluations


@router.get("/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(
    evaluation_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific evaluation."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(Evaluation).where(
            Evaluation.id == evaluation_id,
            Evaluation.tenant_id == ctx.tenant_id,
        )
    )
    evaluation = result.scalar_one_or_none()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found",
        )
    
    return evaluation


@router.get("/{evaluation_id}/questions", response_model=List[QuestionResponse])
async def get_evaluation_questions(
    evaluation_id: UUID,
    include_answers: bool = Query(False),
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get questions for an evaluation."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(Question).where(Question.evaluation_id == evaluation_id)
    )
    questions = list(result.scalars().all())
    
    # Check if user has access to answers
    # Teachers can see answers, students cannot
    can_see_answers = ctx.user.role.value in ["superadmin", "academy_admin", "teacher"]
    
    formatted = []
    for q in questions:
        options = None
        if q.options:
            import json
            options = json.loads(q.options)
        
        response = QuestionResponse(
            id=q.id,
            question_text=q.question_text,
            question_type=q.question_type.value if hasattr(q.question_type, 'value') else q.question_type,
            difficulty=q.difficulty,
            points=q.points,
            order_index=q.order_index,
            options=options,
        )
        formatted.append(response)
    
    return formatted


@router.post("/{evaluation_id}/start", response_model=EvaluationAttemptResponse)
async def start_evaluation(
    evaluation_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Start an evaluation attempt."""
    service = EvaluationService(db)
    
    try:
        attempt = await service.start_attempt(
            evaluation_id=evaluation_id,
            user_id=ctx.user_id,
            tenant_id=ctx.tenant_id,
        )
        
        return EvaluationAttemptResponse(
            id=attempt.id,
            evaluation_id=attempt.evaluation_id,
            started_at=attempt.started_at,
            completed_at=None,
            score=None,
            passed=None,
            time_spent_seconds=None,
            feedback=None,
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{evaluation_id}/submit")
async def submit_evaluation(
    evaluation_id: UUID,
    submission: EvaluationAttemptSubmit,
    attempt_id: UUID = Query(...),
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Submit evaluation answers."""
    service = EvaluationService(db)
    
    try:
        answers_data = [
            {"question_id": str(a.question_id), "answer_text": a.answer_text}
            for a in submission.answers
        ]
        
        result = await service.submit_attempt(
            attempt_id=attempt_id,
            answers=answers_data,
            tenant_id=ctx.tenant_id,
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{evaluation_id}/publish", status_code=status.HTTP_200_OK)
async def publish_evaluation(
    evaluation_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Publish an evaluation so students can access it."""
    if ctx.user.role.value not in ["superadmin", "academy_admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and teachers can publish evaluations",
        )
    
    from sqlalchemy import select, update
    
    result = await db.execute(
        select(Evaluation).where(
            Evaluation.id == evaluation_id,
            Evaluation.tenant_id == ctx.tenant_id,
        )
    )
    evaluation = result.scalar_one_or_none()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found",
        )
    
    if evaluation.question_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot publish evaluation without questions",
        )
    
    evaluation.is_published = True
    await db.flush()
    
    return {"message": "Evaluation published successfully"}


@router.get("/attempts/my", response_model=List[EvaluationAttemptResponse])
async def get_my_attempts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's evaluation attempts."""
    from sqlalchemy import select
    
    offset = (page - 1) * page_size
    result = await db.execute(
        select(EvaluationAttempt)
        .where(
            EvaluationAttempt.user_id == ctx.user_id,
            EvaluationAttempt.tenant_id == ctx.tenant_id,
        )
        .order_by(EvaluationAttempt.started_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    attempts = list(result.scalars().all())
    
    formatted = []
    for attempt in attempts:
        formatted.append(EvaluationAttemptResponse(
            id=attempt.id,
            evaluation_id=attempt.evaluation_id,
            started_at=attempt.started_at,
            completed_at=attempt.completed_at,
            score=attempt.score,
            passed=attempt.passed,
            time_spent_seconds=attempt.time_spent_seconds,
            feedback=None,  # Would need to fetch from answers
        ))
    
    return formatted