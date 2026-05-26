"""RAG service for query answering with citations."""

from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
import time
import json
import logging
from openai import OpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.rag.vector_store import retrieval_pipeline
from app.models import ChatMessage, ChatSession, ChatInteractionLog

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG-based query answering."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._client = None
    
    def _get_client(self) -> OpenAI:
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client
    
    async def query(
        self,
        tenant_id: UUID,
        user_id: UUID,
        query: str,
        session_id: Optional[UUID] = None,
        document_ids: Optional[List[str]] = None,
        subject_id: Optional[str] = None,
        include_history: bool = True,
    ) -> Dict[str, Any]:
        """
        Process a query through the RAG pipeline.
        
        Returns:
            Dict containing answer, citations, and metadata
        """
        start_time = time.time()
        retrieval_start = time.time()
        
        # Retrieve relevant chunks
        chunks, citations = await retrieval_pipeline.retrieve(
            tenant_id=str(tenant_id),
            query=query,
            document_ids=document_ids,
            subject_id=subject_id,
            top_k=5,
        )
        
        retrieval_time = int((time.time() - retrieval_start) * 1000)
        
        if not chunks:
            # No relevant information found
            return {
                "answer": "No relevant information found in the documents to answer your question. Please try rephrasing or ensure documents have been processed.",
                "citations": [],
                "tokens_used": 0,
                "retrieval_count": 0,
                "retrieval_latency_ms": retrieval_time,
                "total_latency_ms": int((time.time() - start_time) * 1000),
            }
        
        # Build context from retrieved chunks
        context = self._build_context(chunks)
        
        # Build conversation history for context
        history_context = ""
        if session_id and include_history:
            history_context = await self._get_conversation_history(session_id)
        
        # Generate answer with LLM
        llm_start = time.time()
        answer, usage = await self._generate_answer(
            query=query,
            context=context,
            history=history_context,
        )
        llm_time = int((time.time() - llm_start) * 1000)
        
        total_time = int((time.time() - start_time) * 1000)
        
        return {
            "answer": answer,
            "citations": citations,
            "tokens_used": usage.get("total_tokens", 0) if usage else 0,
            "input_tokens": usage.get("prompt_tokens", 0) if usage else 0,
            "output_tokens": usage.get("completion_tokens", 0) if usage else 0,
            "retrieval_count": len(chunks),
            "retrieval_latency_ms": retrieval_time,
            "llm_latency_ms": llm_time,
            "total_latency_ms": total_time,
        }
    
    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved chunks."""
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get("metadata", {})
            source = metadata.get("source", "Unknown")
            page = metadata.get("page")
            
            page_info = f" (page {page})" if page else ""
            context_parts.append(f"[Source {i}]{page_info}:\n{chunk['content']}")
        
        return "\n\n".join(context_parts)
    
    async def _get_conversation_history(self, session_id: UUID) -> str:
        """Get formatted conversation history."""
        result = await self.db.execute(
            ChatMessage.__table__.select()
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(10)
        )
        messages = list(result.scalars().all())
        
        if not messages:
            return ""
        
        history = []
        for msg in reversed(messages):
            role = "User" if msg.role == "user" else "Assistant"
            history.append(f"{role}: {msg.content[:500]}")
        
        return "\n".join(history)
    
    async def _generate_answer(
        self,
        query: str,
        context: str,
        history: str = "",
    ) -> Tuple[str, Optional[Dict[str, int]]]:
        """Generate answer using OpenAI with context injection."""
        client = self._get_client()
        
        system_prompt = """You are an educational AI tutor. Your role is to help students understand their course materials.

Instructions:
1. Answer questions based ONLY on the provided context. Do not make up information.
2. If the context doesn't contain enough information to fully answer the question, say so clearly.
3. Always cite your sources using the format [Source N] where N is the source number.
4. Be educational and supportive in your responses.
5. Break down complex concepts in an easy-to-understand way.
6. If the context includes page numbers, mention them in your answer.

Context format:
[Source 1] (page X):
<content>

[Source 2] (page Y):
<content>
"""
        
        user_message = f"Question: {query}\n\nContext:\n{context}"
        if history:
            user_message = f"Previous conversation:\n{history}\n\n{user_message}"
        
        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.3,
                max_tokens=1000,
            )
            
            answer = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
            
            return answer, usage
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise
    
    async def stream_query(
        self,
        tenant_id: UUID,
        user_id: UUID,
        query: str,
        session_id: Optional[UUID] = None,
        document_ids: Optional[List[str]] = None,
        subject_id: Optional[str] = None,
    ):
        """
        Stream a query response using Server-Sent Events.
        
        Yields:
            Chunks of the response as they become available
        """
        import asyncio
        
        start_time = time.time()
        
        # First, retrieve chunks
        chunks, citations = await retrieval_pipeline.retrieve(
            tenant_id=str(tenant_id),
            query=query,
            document_ids=document_ids,
            subject_id=subject_id,
            top_k=5,
        )
        
        retrieval_time = int((time.time() - start_time) * 1000)
        
        if not chunks:
            yield {"type": "done", "data": "No relevant information found.", "citations": []}
            return
        
        # Build context
        context = self._build_context(chunks)
        
        # Build messages
        system_prompt = """You are an educational AI tutor. Answer based ONLY on the provided context.
Cite sources using [Source N] format. If context is insufficient, say so."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ]
        
        client = self._get_client()
        
        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=1000,
                stream=True,
            )
            
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    full_response += text
                    yield {"type": "token", "data": text}
            
            total_time = int((time.time() - start_time) * 1000)
            yield {
                "type": "done",
                "data": full_response,
                "citations": citations,
                "latency_ms": total_time,
            }
            
        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            yield {"type": "error", "data": str(e)}