from typing import Optional, List
from app.core.settings import settings
from app.services.groq_service import get_groq_service
import time


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
        """Process a RAG query using Groq."""
        start_time = time.time()
        
        # Build system prompt for educational context
        system_prompt = {
            "role": "system",
            "content": """Eres C3PO, un tutor educativo de IA. Tu objetivo es ayudar a los estudiantes a aprender 
            y comprender diversos temas académicos. Proporciona explicaciones claras, precisas y didacticas.
            
            Cuando respondas:
            - Usa un lenguaje claro y accesible
            - Incluye ejemplos prácticos cuando sea útil
            - Si no estás seguro de algo, sé honesto al respecto
            - Puedes citar fuentes cuando sea relevante
            
            Si no tienes información específica sobre un documento, usa tu conocimiento general para ayudar al estudiante."""
        }
        
        # Build user message
        user_message = {
            "role": "user",
            "content": query
        }
        
        # Add context about documents if available
        if document_ids:
            user_message["content"] = f"""El usuario pregunta sobre documentos específicos.
            
            Pregunta del usuario: {query}
            
            Proporciona una respuesta educativa basada en tu conocimiento del tema."""
        
        messages = [system_prompt, user_message]
        
        # Get response from Groq
        response = self.groq_service.chat(messages)
        
        end_time = time.time()
        total_latency_ms = int((end_time - start_time) * 1000)
        
        return {
            "answer": response["content"],
            "sources": [],
            "citations": [],
            "input_tokens": response.get("usage", {}).get("prompt_tokens", 0),
            "output_tokens": response.get("usage", {}).get("completion_tokens", 0),
            "tokens_used": response.get("usage", {}).get("total_tokens", 0),
            "total_latency_ms": total_latency_ms,
            "llm_latency_ms": total_latency_ms,
            "retrieval_count": 0,
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
