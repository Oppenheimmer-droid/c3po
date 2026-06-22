"""
RAG Service - Production-ready Retrieval-Augmented Generation for educational AI.
Combines vector search with LLM for accurate, cited responses.
"""

import time
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from app.services.groq_service import get_groq_service, GroqService
from app.services.openai_service import get_openai_service, OpenAIService
from app.rag.vector_store import retrieval_pipeline, VectorStore

logger = logging.getLogger(__name__)


class AIProvider(str, Enum):
    """Available AI providers for RAG."""
    GROQ = "groq"
    OPENAI = "openai"


class RAGService:
    """
    Production-ready RAG service for educational AI tutoring.
    
    Features:
    - Multi-provider support (Groq, OpenAI)
    - Streaming responses
    - Citation tracking
    - Token usage reporting
    - Fallback mechanisms
    """
    
    SYSTEM_PROMPT = """Eres C3PO, un tutor educativo de IA especializado en ayudar a estudiantes.
Tu objetivo es facilitar el aprendizaje de manera clara, precisa y didactica.

Principios de respuesta:
- Usa lenguaje claro y accesible
- Incluye ejemplos practicos cuando sea util
- Estructura las respuestas con listas cuando aplique
- Si no estas seguro, se honesto y explicalo
- Cite fuentes cuando respondas sobre documentos
- Anima al estudiante a hacer preguntas de seguimiento"""

    def __init__(self, db=None, provider: Optional[AIProvider] = None):
        self.db = db
        if provider:
            self.provider = provider
        else:
            from app.core.settings import settings
            provider_str = getattr(settings, "AI_PROVIDER", "groq").lower()
            self.provider = AIProvider(provider_str)
        self._groq_service = None
        self._openai_service = None
        self._vector_store = None
    
    @property
    def groq_service(self) -> GroqService:
        if self._groq_service is None:
            self._groq_service = get_groq_service()
        return self._groq_service
    
    @property
    def openai_service(self) -> OpenAIService:
        if self._openai_service is None:
            self._openai_service = get_openai_service()
        return self._openai_service
    
    @property
    def vector_store(self) -> VectorStore:
        if self._vector_store is None:
            self._vector_store = VectorStore()
        return self._vector_store
    
    def _get_ai_service(self):
        if self.provider == AIProvider.OPENAI:
            return self.openai_service
        return self.groq_service
    
    async def query(
        self,
        tenant_id: str,
        user_id: str,
        query: str,
        session_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
        subject_id: Optional[str] = None,
        include_history: bool = True,
        top_k: int = 4,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """Process a RAG query with vector retrieval and LLM generation."""
        start_time = time.time()
        
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not query:
            raise ValueError("query cannot be empty")
        
        context_chunks = []
        citations = []
        retrieval_latency_ms = 0
        
        retrieval_start = time.time()
        try:
            retrieval_result = retrieval_pipeline(
                query=query,
                tenant_id=tenant_id,
                top_k=top_k,
            )
            context_chunks = retrieval_result.get("chunks", [])
            retrieval_latency_ms = int((time.time() - retrieval_start) * 1000)
            
            for i, chunk in enumerate(context_chunks):
                chunk_id = chunk.get("id", f"chunk_{i}")
                metadata = chunk.get("metadata", {})
                source = metadata.get("source", metadata.get("document_id", "document"))
                page = metadata.get("page")
                
                citations.append({
                    "chunk_id": chunk_id,
                    "source": source,
                    "page": page,
                    "content_preview": chunk.get("content", "")[:100],
                })
                
        except Exception as e:
            logger.warning(f"Vector retrieval failed: {e}")
            context_chunks = []
        
        messages = self._build_messages(query, context_chunks)
        
        llm_start = time.time()
        ai_service = self._get_ai_service()
        
        try:
            response = ai_service.chat(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except RuntimeError as e:
            logger.error(f"AI service error: {e}")
            return self._fallback_response(query, str(e), time.time() - start_time)
        
        llm_latency_ms = int((time.time() - llm_start) * 1000)
        total_latency_ms = int((time.time() - start_time) * 1000)
        
        usage = response.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        tokens_used = usage.get("total_tokens", input_tokens + output_tokens)
        
        return {
            "answer": response["content"],
            "sources": [chunk.get("content", "")[:150] + "..." for chunk in context_chunks[:3]],
            "citations": citations,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "tokens_used": tokens_used,
            "retrieval_count": len(context_chunks),
            "retrieval_latency_ms": retrieval_latency_ms,
            "llm_latency_ms": llm_latency_ms,
            "total_latency_ms": total_latency_ms,
            "model": response.get("model", "unknown"),
            "provider": self.provider.value,
        }
    
    def _build_messages(self, query: str, context_chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Build messages for LLM with context."""
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        
        if context_chunks:
            context_parts = []
            for i, chunk in enumerate(context_chunks[:3]):
                content = chunk.get("content", "")
                metadata = chunk.get("metadata", {})
                source = metadata.get("source", f"Document {i+1}")
                context_parts.append(f"[{source}]:\n{content}")
            
            context_str = "\n\n---\n\n".join(context_parts)
            
            user_content = f"""Contexto relevante de documentos:

{context_str}

---
Pregunta del estudiante: {query}

Responde basandote en el contexto proporcionado."""
        else:
            user_content = query
        
        messages.append({"role": "user", "content": user_content})
        return messages
    
    def _fallback_response(self, query: str, error: str, elapsed: float) -> Dict[str, Any]:
        """Generate a fallback response when services are unavailable."""
        return {
            "answer": f"El servicio de IA no esta disponible. Error: {error}",
            "sources": [],
            "citations": [],
            "input_tokens": 0,
            "output_tokens": 0,
            "tokens_used": 0,
            "retrieval_count": 0,
            "retrieval_latency_ms": 0,
            "llm_latency_ms": 0,
            "total_latency_ms": int(elapsed * 1000),
            "model": "fallback",
            "provider": "none",
            "error": error,
        }
    
    async def chat(self, message: str, user_id: str = None, temperature: float = 0.7) -> Dict[str, Any]:
        """Simple chat without RAG retrieval."""
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]
        
        ai_service = self._get_ai_service()
        response = ai_service.chat(messages, temperature=temperature)
        
        return {
            "answer": response["content"],
            "sources": [],
            "citations": [],
            "tokens_used": response.get("usage", {}).get("total_tokens", 0),
        }
