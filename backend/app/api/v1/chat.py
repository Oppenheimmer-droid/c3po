"""Chat API endpoints for RAG interactions."""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import json
import logging

from app.core.tenant import get_tenant_context
from app.core.database import get_db
from app.services.rag_service import RAGService
from app.models import ChatSession, ChatMessage, ChatInteractionLog
from app.schemas import (
    ChatSessionCreate, ChatSessionResponse, MessageCreate, MessageResponse, ChatStreamResponse,
)

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    session_data: ChatSessionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new chat session."""
    ctx = await get_tenant_context()
    session = ChatSession(
        tenant_id=ctx.tenant_id,
        user_id=ctx.user_id,
        title=session_data.title,
        document_id=session_data.document_id,
        subject_id=session_data.subject_id,
    )
    
    db.add(session)
    await db.flush()
    await db.refresh(session)
    
    return session


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def list_chat_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List chat sessions for the current user."""
    ctx = await get_tenant_context()
    offset = (page - 1) * page_size
    
    result = await db.execute(
        select(ChatSession)
        .where(
            ChatSession.tenant_id == ctx.tenant_id,
            ChatSession.user_id == ctx.user_id,
        )
        .order_by(ChatSession.updated_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    sessions = list(result.scalars().all())
    
    return sessions


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific chat session."""
    ctx = await get_tenant_context()
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.tenant_id == ctx.tenant_id,
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )
    
    return session


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a chat session."""
    ctx = await get_tenant_context()
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.tenant_id == ctx.tenant_id,
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )
    
    # Only owner or admin can delete
    if session.user_id != ctx.user_id and ctx.user.role.value not in ["superadmin", "academy_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this session",
        )
    
    await db.delete(session)
    await db.flush()
    
    return None


@router.post("/sessions/{session_id}/messages", response_model=MessageResponse)
async def send_message(
    session_id: UUID,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
):
    """Send a message and get a response."""
    ctx = await get_tenant_context()
    # Verify session exists and belongs to tenant
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.tenant_id == ctx.tenant_id,
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )
    
    # Create user message
    user_message = ChatMessage(
        session_id=session_id,
        tenant_id=ctx.tenant_id,
        user_id=ctx.user_id,
        role="user",
        content=message_data.content,
    )
    db.add(user_message)
    await db.flush()
    
    # Process query through RAG
    service = RAGService(db)
    
    # Build document filter
    document_ids = [str(session.document_id)] if session.document_id else None
    subject_id = str(session.subject_id) if session.subject_id else None
    
    try:
        result = await service.query(
            tenant_id=ctx.tenant_id,
            user_id=ctx.user_id,
            query=message_data.content,
            session_id=session_id,
            document_ids=document_ids,
            subject_id=subject_id,
        )
        
        # Create assistant message
        assistant_message = ChatMessage(
            session_id=session_id,
            tenant_id=ctx.tenant_id,
            user_id=ctx.user_id,
            role="assistant",
            content=result["answer"],
            citations=json.dumps(result["citations"]) if result["citations"] else None,
            input_tokens=result.get("input_tokens", 0),
            output_tokens=result.get("output_tokens", 0),
            retrieval_count=result.get("retrieval_count", 0),
            retrieval_latency_ms=result.get("retrieval_latency_ms"),
            total_latency_ms=result.get("total_latency_ms"),
        )
        db.add(assistant_message)
        
        # Update session stats
        session.message_count += 2
        session.total_tokens += result.get("tokens_used", 0)
        session.last_message_at = datetime.now(timezone.utc)
        
        await db.flush()
        await db.refresh(assistant_message)
        
        # Log interaction
        log = ChatInteractionLog(
            tenant_id=ctx.tenant_id,
            user_id=ctx.user_id,
            message_id=assistant_message.id,
            llm_model="gpt-4o-mini",
            prompt_tokens=result.get("input_tokens", 0),
            completion_tokens=result.get("output_tokens", 0),
            llm_latency_ms=result.get("llm_latency_ms"),
            retrieved_chunk_ids=json.dumps([c["chunk_id"] for c in result["citations"]]) if result["citations"] else None,
        )
        db.add(log)
        await db.flush()
        
        # Parse citations
        citations = []
        if result["citations"]:
            for c in result["citations"]:
                citations.append({
                    "chunk_id": c.get("chunk_id"),
                    "source": c.get("source", "Unknown"),
                    "page": c.get("page"),
                })
        
        return MessageResponse(
            id=assistant_message.id,
            role="assistant",
            content=result["answer"],
            citations=citations if citations else None,
            input_tokens=result.get("input_tokens", 0),
            output_tokens=result.get("output_tokens", 0),
            created_at=assistant_message.created_at,
        )
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_BAD_REQUEST,
            detail=f"Error processing query: {str(e)}",
        )


@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(
    session_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get messages for a chat session."""
    ctx = await get_tenant_context()
    result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.session_id == session_id,
            ChatMessage.tenant_id == ctx.tenant_id,
        )
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
    )
    messages = list(result.scalars().all())
    
    formatted_messages = []
    for msg in messages:
        citations = None
        if msg.citations:
            try:
                citations_data = json.loads(msg.citations)
                citations = [
                    {
                        "chunk_id": c.get("chunk_id"),
                        "source": c.get("source", "Unknown"),
                        "page": c.get("page"),
                    }
                    for c in citations_data
                ]
            except:
                pass
        
        formatted_messages.append(MessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            citations=citations,
            input_tokens=msg.input_tokens,
            output_tokens=msg.output_tokens,
            created_at=msg.created_at,
        ))
    
    return formatted_messages


@router.post("/query")
async def query_rag(
    query: str,
    document_ids: Optional[str] = Query(None),  # Comma-separated
    subject_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Simple RAG query endpoint (no session required)."""
    ctx = await get_tenant_context()
    doc_ids = document_ids.split(",") if document_ids else None
    
    service = RAGService(db)
    result = await service.query(
        tenant_id=ctx.tenant_id,
        user_id=ctx.user_id,
        query=query,
        document_ids=doc_ids,
        subject_id=str(subject_id) if subject_id else None,
        include_history=False,
    )
    
    return {
        "answer": result["answer"],
        "citations": result["citations"],
        "tokens_used": result["tokens_used"],
    }