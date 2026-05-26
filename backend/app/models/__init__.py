"""All database models."""

from app.core.database import Base

# Import all models to register them with Base
from app.models.auth import Tenant, User, UserSession, RefreshToken, UserRole, TenantStatus
from app.models.documents import Subject, Topic, Document, DocumentChunk
from app.models.chat import ChatSession, ChatMessage, ChatInteractionLog
from app.models.evaluations import (
    Evaluation, Question, EvaluationAttempt, Answer,
    EvaluationType, QuestionType
)

__all__ = [
    "Base",
    "Tenant", "User", "UserSession", "RefreshToken", "UserRole", "TenantStatus",
    "Subject", "Topic", "Document", "DocumentChunk",
    "ChatSession", "ChatMessage", "ChatInteractionLog",
    "Evaluation", "Question", "EvaluationAttempt", "Answer",
    "EvaluationType", "QuestionType",
]