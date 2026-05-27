"""Evaluation and quiz models."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, DateTime, Integer, Float, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.core.database import Base
import enum
import uuid


class EvaluationType(str, enum.Enum):
    """Type of evaluation."""
    QUIZ = "quiz"
    EXAM = "exam"
    PRACTICE = "practice"


class QuestionType(str, enum.Enum):
    """Type of question."""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"


class Evaluation(Base):
    """Evaluation/Quiz generated from documents."""
    
    __tablename__ = "evaluations"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    
    # Evaluation info
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evaluation_type: Mapped[EvaluationType] = mapped_column(String(50), default=EvaluationType.QUIZ, nullable=False)
    
    # Settings
    time_limit_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    passing_score: Mapped[int] = mapped_column(Integer, default=60)  # percentage
    difficulty: Mapped[Optional[int]] = mapped_column(Integer, default=1)  # 1-5
    
    # Stats
    question_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_score: Mapped[Optional[Float]] = mapped_column(Float, nullable=True)
    
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    questions: Mapped[list["Question"]] = relationship(
        back_populates="evaluation", cascade="all, delete-orphan"
    )
    attempts: Mapped[list["EvaluationAttempt"]] = relationship(
        back_populates="evaluation", cascade="all, delete-orphan"
    )
    document: Mapped["Document"] = relationship(back_populates="evaluations")


class Question(Base):
    """Question within an evaluation."""
    
    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=uuid.uuid4)
    evaluation_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Question content
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(String(50), nullable=False)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Shown after answer
    
    # For chunk reference and difficulty
    source_chunk_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)
    points: Mapped[int] = mapped_column(Integer, default=1)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    
    # Settings
    options: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON for multiple choice
    correct_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    acceptable_answers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON for short answer variations
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    evaluation: Mapped["Evaluation"] = relationship(back_populates="questions")
    answers: Mapped[list["Answer"]] = relationship(back_populates="question")


class EvaluationAttempt(Base):
    """Student attempt at an evaluation."""
    
    __tablename__ = "evaluation_attempts"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    evaluation_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Attempt info
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    time_spent_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Score
    score: Mapped[Optional[Float]] = mapped_column(Float, nullable=True)  # percentage
    passed: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # Feedback
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # AI-generated feedback
    
    # Token usage for grading
    grading_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    evaluation: Mapped["Evaluation"] = relationship(back_populates="attempts")
    answers: Mapped[list["Answer"]] = relationship(back_populates="attempt", cascade="all, delete-orphan")


class Answer(Base):
    """Student's answer to a question."""
    
    __tablename__ = "answers"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=uuid.uuid4)
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("evaluation_attempts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Answer content
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Grading
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=True)
    points_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ai_grade_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # AI feedback for short answer
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    attempt: Mapped["EvaluationAttempt"] = relationship(back_populates="answers")
    question: Mapped["Question"] = relationship(back_populates="answers")