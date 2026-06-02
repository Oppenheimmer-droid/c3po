"""Pydantic schemas for request/response validation."""

from app.schemas.schemas import (
    # Tenant schemas
    TenantCreate, TenantUpdate, TenantResponse,
    # User schemas
    UserCreate, UserUpdate, UserResponse, UserMeResponse,
    # Auth schemas
    LoginRequest, TokenResponse, RefreshRequest, ChangePasswordRequest,
    PasswordResetRequest, SetPasswordRequest,
    # Document schemas
    DocumentMetadata, DocumentResponse, DocumentListResponse, DocumentChunkResponse,
    # Chat schemas
    ChatSessionCreate, ChatSessionResponse, MessageCreate, MessageResponse,
    ChatStreamResponse, Citation,
    # Evaluation schemas
    EvaluationCreate, EvaluationResponse, QuestionResponse,
    EvaluationAttemptStart, AnswerSubmit, EvaluationAttemptSubmit, EvaluationAttemptResponse,
    # Analytics schemas
    StudentProgress, TenantAnalytics,
    # Common schemas
    HealthResponse, ErrorResponse, PaginatedResponse,
)

__all__ = [
    "TenantCreate", "TenantUpdate", "TenantResponse",
    "UserCreate", "UserUpdate", "UserResponse", "UserMeResponse",
    "LoginRequest", "TokenResponse", "RefreshRequest", "ChangePasswordRequest",
    "PasswordResetRequest", "SetPasswordRequest",
    "DocumentMetadata", "DocumentResponse", "DocumentListResponse", "DocumentChunkResponse",
    "ChatSessionCreate", "ChatSessionResponse", "MessageCreate", "MessageResponse",
    "ChatStreamResponse", "Citation",
    "EvaluationCreate", "EvaluationResponse", "QuestionResponse",
    "EvaluationAttemptStart", "AnswerSubmit", "EvaluationAttemptSubmit", "EvaluationAttemptResponse",
    "StudentProgress", "TenantAnalytics",
    "HealthResponse", "ErrorResponse", "PaginatedResponse",
]