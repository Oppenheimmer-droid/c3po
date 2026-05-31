"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, str, ConfigDict, Field


# ────────────────────────────────
# Base schemas
# ────────────────────────────────

class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""
    created_at: datetime
    updated_at: Optional[datetime] = None


# ────────────────────────────────
# Tenant schemas
# ────────────────────────────────

class TenantBase(BaseModel):
    """Base tenant schema."""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")


class TenantCreate(TenantBase):
    """Schema for creating a tenant."""
    settings: Optional[dict] = None


class TenantUpdate(BaseModel):
    """Schema for updating a tenant."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = None
    settings: Optional[dict] = None


class TenantResponse(TenantBase, TimestampMixin):
    """Schema for tenant response."""
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    status: str
    settings: Optional[dict] = None


# ────────────────────────────────
# User schemas
# ────────────────────────────────

class UserBase(BaseModel):
    """Base user schema."""
    email: str
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: str = "student"


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserResponse(UserBase, TimestampMixin):
    """Schema for user response."""
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None


class UserMeResponse(BaseModel):
    """Schema for current user info."""
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    first_name: str
    last_name: str
    role: str
    tenant_id: UUID
    tenant_name: str


# ────────────────────────────────
# Auth schemas
# ────────────────────────────────

class LoginRequest(BaseModel):
    """Schema for login request."""
    email: str
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Schema for changing password."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class PasswordResetRequest(BaseModel):
    """Schema for requesting password reset."""
    email: str


class SetPasswordRequest(BaseModel):
    """Schema for setting new password (after reset)."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


# ────────────────────────────────
# Document schemas
# ────────────────────────────────

class DocumentMetadata(BaseModel):
    """Metadata for document upload."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    subject_id: Optional[UUID] = None
    topic_id: Optional[UUID] = None
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    tags: Optional[List[str]] = None


class DocumentResponse(TimestampMixin):
    """Schema for document response."""
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    title: str
    original_filename: str
    file_size: int
    mime_type: str
    status: str
    page_count: Optional[int] = None
    chunk_count: Optional[int] = None
    subject_id: Optional[UUID] = None
    topic_id: Optional[UUID] = None
    difficulty: Optional[int] = None


class DocumentListResponse(BaseModel):
    """Schema for paginated document list."""
    items: List[DocumentResponse]
    total: int
    page: int
    page_size: int
    pages: int


class DocumentChunkResponse(BaseModel):
    """Schema for document chunk."""
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    content: str
    chunk_index: int
    page_number: Optional[int] = None


# ────────────────────────────────
# Chat schemas
# ────────────────────────────────

class ChatSessionCreate(BaseModel):
    """Schema for creating a chat session."""
    title: str = Field(..., min_length=1, max_length=255)
    document_id: Optional[UUID] = None
    subject_id: Optional[UUID] = None


class ChatSessionResponse(TimestampMixin):
    """Schema for chat session response."""
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    user_id: UUID
    title: str
    document_id: Optional[UUID] = None
    message_count: int
    is_archived: bool
    last_message_at: Optional[datetime] = None


class MessageCreate(BaseModel):
    """Schema for creating a chat message."""
    content: str = Field(..., min_length=1, max_length=5000)


class Citation(BaseModel):
    """Schema for a citation."""
    chunk_id: UUID
    source: str
    page: Optional[int] = None
    text: Optional[str] = None


class MessageResponse(BaseModel):
    """Schema for chat message response."""
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    role: str
    content: str
    citations: Optional[List[Citation]] = None
    input_tokens: int
    output_tokens: int
    created_at: datetime


class ChatStreamResponse(BaseModel):
    """Schema for streaming chat response."""
    type: str  # token, citation, done, error
    data: Optional[str] = None
    citations: Optional[List[Citation]] = None


# ────────────────────────────────
# Evaluation schemas
# ────────────────────────────────

class EvaluationCreate(BaseModel):
    """Schema for creating an evaluation."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    document_id: UUID
    question_count: int = Field(default=10, ge=1, le=50)
    difficulty: Optional[int] = Field(default=1, ge=1, le=5)
    evaluation_type: str = "quiz"
    time_limit_minutes: Optional[int] = None
    passing_score: int = Field(default=60, ge=0, le=100)


class EvaluationResponse(TimestampMixin):
    """Schema for evaluation response."""
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    description: Optional[str]
    document_id: UUID
    evaluation_type: str
    question_count: int
    time_limit_minutes: Optional[int]
    passing_score: int
    difficulty: int
    is_published: bool
    total_attempts: int
    avg_score: Optional[float]


class QuestionResponse(BaseModel):
    """Schema for question response."""
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    question_text: str
    question_type: str
    difficulty: int
    points: int
    order_index: int
    options: Optional[List[dict]] = None


class EvaluationAttemptStart(BaseModel):
    """Schema for starting an evaluation attempt."""
    pass


class AnswerSubmit(BaseModel):
    """Schema for submitting an answer."""
    question_id: UUID
    answer_text: str


class EvaluationAttemptSubmit(BaseModel):
    """Schema for submitting answers."""
    answers: List[AnswerSubmit]


class EvaluationAttemptResponse(BaseModel):
    """Schema for evaluation attempt response."""
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    evaluation_id: UUID
    started_at: datetime
    completed_at: Optional[datetime]
    score: Optional[float]
    passed: Optional[bool]
    time_spent_seconds: Optional[int]
    feedback: Optional[str]
    answers: Optional[List[dict]] = None


# ────────────────────────────────
# Analytics schemas
# ────────────────────────────────

class StudentProgress(BaseModel):
    """Schema for student progress."""
    student_id: UUID
    total_evaluations: int
    completed_evaluations: int
    avg_score: float
    weak_topics: List[dict]
    strong_topics: List[dict]


class TenantAnalytics(BaseModel):
    """Schema for tenant analytics."""
    total_users: int
    total_documents: int
    total_chats: int
    total_evaluations: int
    total_tokens_used: int
    avg_chat_score: float


# ────────────────────────────────
# Common schemas
# ────────────────────────────────

class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str
    version: str
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Schema for error response."""
    detail: str
    code: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Base schema for paginated responses."""
    total: int
    page: int
    page_size: int
    pages: int