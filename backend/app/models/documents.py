"""Document and subject models."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Subject(Base):
    """Subject configuration (e.g., Mathematics, Physics)."""
    
    __tablename__ = "subjects"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default="gen_random_uuid()")
    tenant_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "MATH101"
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    grade_levels: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # JSON array
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    documents: Mapped[list["Document"]] = relationship(back_populates="subject", cascade="all, delete-orphan")
    topics: Mapped[list["Topic"]] = relationship(back_populates="subject", cascade="all, delete-orphan")


class Topic(Base):
    """Topic within a subject (e.g., "Quadratic Equations")."""
    
    __tablename__ = "topics"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default="gen_random_uuid()")
    subject_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty: Mapped[Optional[int]] = mapped_column(Integer, default=1)  # 1-5 scale
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    subject: Mapped["Subject"] = relationship(back_populates="topics")
    documents: Mapped[list["Document"]] = relationship(back_populates="topic")


class Document(Base):
    """Uploaded document with metadata."""
    
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default="gen_random_uuid()")
    tenant_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subject_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True, index=True
    )
    topic_id: Mapped[Optional[UUID]] = mapped_column(
        UUID, ForeignKey("topics.id", ondelete="SET NULL"), nullable=True, index=True
    )
    uploaded_by: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    
    # File info
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    
    # Processing status
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    chunk_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty: Mapped[Optional[int]] = mapped_column(Integer, default=1)  # 1-5 scale
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    subject: Mapped[Optional["Subject"]] = relationship(back_populates="documents")
    topic: Mapped[Optional["Topic"]] = relationship(back_populates="documents")
    chunks: Mapped[list["DocumentChunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    chat_sessions: Mapped[list["ChatSession"]] = relationship(back_populates="document")
    evaluations: Mapped[list["Evaluation"]] = relationship(back_populates="document")


class DocumentChunk(Base):
    """Document chunk for RAG embedding."""
    
    __tablename__ = "document_chunks"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default="gen_random_uuid()")
    document_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tenant_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Chunk content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Embedding reference (stored in ChromaDB)
    vector_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # Metadata
    start_char: Mapped[int] = mapped_column(Integer, nullable=False)
    end_char: Mapped[int] = mapped_column(Integer, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    document: Mapped["Document"] = relationship(back_populates="chunks")