from typing import Optional, List
from app.core.settings import settings
from app.services.groq_service import get_groq_service
from app.rag.vector_store import retrieval_pipeline
import time
import logging

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self, db=None):
        self.db = db
        self.groq_service = get_groq_service()

    async def query(
        self,
        tenant_id: str,
        user_id: str,
        query: str,
        session_id=None,
        document_ids: Optional[List[str]] = None,
        subject_id: Optional[str] = None,
        include_history: bool = True,
    ) -> dict:
        """Process a RAG query using Groq with vector retrieval."""
        start_time = time.time()

        # Try vector retrieval first
        context_chunks = []
        citations = []
        
        try:
            if tenant_id and tenant_id != "dummy-tenant":
                retrieval_result = retrieval_pipeline(
                    query=query,
                    tenant_id=tenant_id,
                    top_k=4
                )
                context_chunks = retrieval_result.get("chunks", [])
                citations = [
                    {"chunk_id": chunk.get("id", f"chunk_{i}"), "source": "document", "page": None}
                    for i, chunk in enumerate(context_chunks)
                ]
        except Exception as e:
            logger.warning(f"Vector retrieval failed: {e}")

        # Build system prompt for educational context
        system_content = """Eres C3PO, un tutor educativo de IA. Tu objetivo es ayudar a los estudiantes a aprender
y comprender diversos temas académicos. Proporciona explicaciones claras, precisas y didacticas.

Cuando respondas:
- Usa un lenguaje claro y accesible
- Incluye ejemplos prácticos cuando sea útil
- Si no estás seguro de algo, sé honesto al respecto
- Puedes citar fuentes cuando sea relevante

Si no tienes información específica sobre un documento, usa tu conocimiento general para ayudar al estudiante."""

        # Add context if available
        if context_chunks:
            context_str = "\n\n---\n\n".join([
                f"[Documento {i+1}]: {chunk['content'][:500]}..."
                for i, chunk in enumerate(context_chunks[:3])
            ])
            user_content = f"""Contexto relevante de documentos del estudiante:

{context_str}

Pregunta: {query}

Responde basándote en el contexto proporcionado cuando sea relevante."""
        else:
            user_content = query

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]

        # Get response from Groq
        response = self.groq_service.chat(messages)

        end_time = time.time()
        total_latency_ms = int((end_time - start_time) * 1000)

        return {
            "answer": response["content"],
            "sources": [chunk.get("content", "")[:100] + "..." for chunk in context_chunks[:3]],
            "citations": citations,
            "input_tokens": response.get("usage", {}).get("prompt_tokens", 0),
            "output_tokens": response.get("usage", {}).get("completion_tokens", 0),
            "tokens_used": response.get("usage", {}).get("total_tokens", 0),
            "total_latency_ms": total_latency_ms,
            "llm_latency_ms": total_latency_ms,
            "retrieval_count": len(context_chunks),
        }

    async def chat(self, message: str, user_id: str = None) -> dict:
        """Simple chat method for non-RAG queries."""
        groq_response = self.groq_service.chat([
            {"role": "system", "content": "Eres C3PO, un tutor educativo de IA."},
            {"role": "user", "content": message}
        ])

        return {
            "answer": groq_response["content"],
            "sources": []
        }
