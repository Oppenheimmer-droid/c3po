"""Analytics API endpoints."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, TenantContext, get_tenant_context, require_admin_or_teacher
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview")
async def get_tenant_overview(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get overview metrics for the tenant."""
    service = AnalyticsService(db)
    return await service.get_tenant_overview(ctx.tenant_id)


@router.get("/students/me")
async def get_my_progress(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get current student's progress statistics."""
    service = AnalyticsService(db)
    return await service.get_student_progress(ctx.user_id, ctx.tenant_id)


@router.get("/students/{student_id}")
async def get_student_progress(
    student_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get progress for a specific student (admin/teacher only)."""
    if ctx.user.role.value not in ["superadmin", "academy_admin", "teacher"]:
        return {"error": "Only teachers and admins can view student progress"}
    
    service = AnalyticsService(db)
    return await service.get_student_progress(student_id, ctx.tenant_id)


@router.get("/teacher/overview")
async def get_teacher_overview(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get overview for the current teacher."""
    if ctx.user.role.value not in ["superadmin", "academy_admin", "teacher"]:
        return {"error": "Only teachers and admins can access this endpoint"}
    
    service = AnalyticsService(db)
    return await service.get_teacher_class_overview(ctx.user_id, ctx.tenant_id)


@router.get("/documents/{document_id}/stats")
async def get_document_stats(
    document_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get statistics for a specific document."""
    service = AnalyticsService(db)
    return await service.get_document_stats(document_id, ctx.tenant_id)


@router.get("/usage")
async def get_usage_over_time(
    days: int = Query(30, ge=1, le=90),
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get usage metrics over time."""
    service = AnalyticsService(db)
    return await service.get_usage_over_time(ctx.tenant_id, days)