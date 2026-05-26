"""Analytics service for metrics and reporting."""

from typing import Dict, List, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    User, Document, ChatSession, ChatMessage, EvaluationAttempt,
    Evaluation, Answer, Tenant
)


class AnalyticsService:
    """Service for generating analytics and reports."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_tenant_overview(self, tenant_id: UUID) -> Dict[str, Any]:
        """Get overview metrics for a tenant."""
        # Count users
        users_result = await self.db.execute(
            select(func.count()).select_from(User).where(User.tenant_id == tenant_id)
        )
        total_users = users_result.scalar() or 0
        
        # Count active users (logged in within 30 days)
        active_users_result = await self.db.execute(
            select(func.count()).select_from(User).where(
                and_(
                    User.tenant_id == tenant_id,
                    User.last_login >= datetime.now(timezone.utc) - timedelta(days=30)
                )
            )
        )
        active_users = active_users_result.scalar() or 0
        
        # Count documents
        docs_result = await self.db.execute(
            select(func.count()).select_from(Document).where(
                Document.tenant_id == tenant_id,
                Document.status == "completed"
            )
        )
        total_documents = docs_result.scalar() or 0
        
        # Count chat sessions
        sessions_result = await self.db.execute(
            select(func.count()).select_from(ChatSession).where(
                ChatSession.tenant_id == tenant_id
            )
        )
        total_sessions = sessions_result.scalar() or 0
        
        # Count evaluations
        evals_result = await self.db.execute(
            select(func.count()).select_from(Evaluation).where(
                Evaluation.tenant_id == tenant_id
            )
        )
        total_evaluations = evals_result.scalar() or 0
        
        # Get total tokens used
        tokens_result = await self.db.execute(
            select(func.sum(ChatMessage.output_tokens)).where(
                ChatMessage.tenant_id == tenant_id
            )
        )
        total_tokens = tokens_result.scalar() or 0
        
        # Calculate average evaluation score
        score_result = await self.db.execute(
            select(func.avg(EvaluationAttempt.score)).where(
                EvaluationAttempt.tenant_id == tenant_id,
                EvaluationAttempt.score.isnot(None)
            )
        )
        avg_eval_score = score_result.scalar()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_documents": total_documents,
            "total_chat_sessions": total_sessions,
            "total_evaluations": total_evaluations,
            "total_tokens_used": total_tokens,
            "avg_evaluation_score": round(avg_eval_score, 1) if avg_eval_score else None,
        }
    
    async def get_student_progress(
        self,
        user_id: UUID,
        tenant_id: UUID,
    ) -> Dict[str, Any]:
        """Get detailed progress for a student."""
        # Get all attempts
        attempts_result = await self.db.execute(
            select(EvaluationAttempt).where(
                EvaluationAttempt.user_id == user_id,
                EvaluationAttempt.tenant_id == tenant_id,
            )
        )
        attempts = list(attempts_result.scalars().all())
        
        if not attempts:
            return {
                "total_attempts": 0,
                "completed_attempts": 0,
                "avg_score": 0,
                "best_score": 0,
                "pass_rate": 0,
                "weak_topics": [],
                "strong_topics": [],
            }
        
        completed = [a for a in attempts if a.completed_at]
        scores = [a.score for a in completed if a.score is not None]
        
        passed = sum(1 for a in completed if a.passed)
        
        # Get weak/strong topics from answers
        weak_topics = []
        strong_topics = []
        
        return {
            "total_attempts": len(attempts),
            "completed_attempts": len(completed),
            "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
            "best_score": max(scores) if scores else 0,
            "pass_rate": round(passed / len(completed) * 100, 1) if completed else 0,
            "weak_topics": weak_topics,
            "strong_topics": strong_topics,
        }
    
    async def get_teacher_class_overview(
        self,
        teacher_id: UUID,
        tenant_id: UUID,
    ) -> Dict[str, Any]:
        """Get overview for a teacher's classes/students."""
        # Count students (users with student role)
        students_result = await self.db.execute(
            select(func.count()).select_from(User).where(
                User.tenant_id == tenant_id,
                User.role == "student"
            )
        )
        total_students = students_result.scalar() or 0
        
        # Count evaluations created by teacher
        evals_result = await self.db.execute(
            select(func.count()).select_from(Evaluation).where(
                Evaluation.tenant_id == tenant_id,
                Evaluation.created_by == teacher_id,
            )
        )
        teacher_evals = evals_result.scalar() or 0
        
        # Average scores across teacher's evaluations
        score_result = await self.db.execute(
            select(func.avg(EvaluationAttempt.score)).join(
                Evaluation, EvaluationAttempt.evaluation_id == Evaluation.id
            ).where(
                EvaluationAttempt.tenant_id == tenant_id,
                Evaluation.created_by == teacher_id,
                EvaluationAttempt.score.isnot(None)
            )
        )
        avg_score = score_result.scalar()
        
        # Recent activity (last 7 days)
        recent_sessions = await self.db.execute(
            select(func.count()).select_from(ChatSession).where(
                ChatSession.tenant_id == tenant_id,
                ChatSession.created_at >= datetime.now(timezone.utc) - timedelta(days=7)
            )
        )
        recent_count = recent_sessions.scalar() or 0
        
        return {
            "total_students": total_students,
            "evaluations_created": teacher_evals,
            "avg_student_score": round(avg_score, 1) if avg_score else None,
            "active_students_7d": recent_count,
        }
    
    async def get_document_stats(
        self,
        document_id: UUID,
        tenant_id: UUID,
    ) -> Dict[str, Any]:
        """Get statistics for a specific document."""
        from app.models import Document
        
        # Get document info
        doc_result = await self.db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.tenant_id == tenant_id,
            )
        )
        document = doc_result.scalar_one_or_none()
        
        if not document:
            return {}
        
        # Count related chat sessions
        sessions_result = await self.db.execute(
            select(func.count()).select_from(ChatSession).where(
                ChatSession.document_id == document_id
            )
        )
        sessions_count = sessions_result.scalar() or 0
        
        # Count messages in those sessions
        messages_result = await self.db.execute(
            select(func.count()).select_from(ChatMessage).where(
                ChatMessage.session_id.in_(
                    select(ChatSession.id).where(ChatSession.document_id == document_id)
                )
            )
        )
        messages_count = messages_result.scalar() or 0
        
        # Count evaluations from this document
        evals_result = await self.db.execute(
            select(func.count()).select_from(Evaluation).where(
                Evaluation.document_id == document_id
            )
        )
        evaluations_count = evals_result.scalar() or 0
        
        return {
            "document_id": str(document_id),
            "title": document.title,
            "status": document.status,
            "chunk_count": document.chunk_count,
            "chat_sessions": sessions_count,
            "chat_messages": messages_count,
            "evaluations": evaluations_count,
        }
    
    async def get_usage_over_time(
        self,
        tenant_id: UUID,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        """Get usage metrics over time."""
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Get daily chat counts
        daily_data = []
        
        for i in range(days):
            day_start = start_date + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            # Count sessions for this day
            sessions_result = await self.db.execute(
                select(func.count()).select_from(ChatSession).where(
                    and_(
                        ChatSession.tenant_id == tenant_id,
                        ChatSession.created_at >= day_start,
                        ChatSession.created_at < day_end,
                    )
                )
            )
            sessions_count = sessions_result.scalar() or 0
            
            # Count messages for this day
            messages_result = await self.db.execute(
                select(func.count()).select_from(ChatMessage).where(
                    and_(
                        ChatMessage.tenant_id == tenant_id,
                        ChatMessage.created_at >= day_start,
                        ChatMessage.created_at < day_end,
                    )
                )
            )
            messages_count = messages_result.scalar() or 0
            
            # Count evaluations for this day
            evals_result = await self.db.execute(
                select(func.count()).select_from(EvaluationAttempt).where(
                    and_(
                        EvaluationAttempt.tenant_id == tenant_id,
                        EvaluationAttempt.started_at >= day_start,
                        EvaluationAttempt.started_at < day_end,
                    )
                )
            )
            evals_count = evals_result.scalar() or 0
            
            daily_data.append({
                "date": day_start.date().isoformat(),
                "chat_sessions": sessions_count,
                "chat_messages": messages_count,
                "evaluation_attempts": evals_count,
            })
        
        return daily_data