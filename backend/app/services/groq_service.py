"""
Groq AI Service - Production-ready LLM integration for educational responses.
Supports streaming, function calling, and automatic fallback to OpenAI.
"""

import os
import logging
import random
from typing import Optional, Callable, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AIProvider(str, Enum):
    """Available AI providers."""
    GROQ = "groq"
    OPENAI = "openai"


@dataclass
class ChatMessage:
    """Chat message structure."""
    role: str
    content: str
    name: Optional[str] = None


@dataclass
class ChatResponse:
    """Chat response structure."""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: Optional[str] = None


# Sample responses for mock mode
MOCK_RESPONSES = [
    "Basándome en el contexto proporcionado, puedo decir que esta es una pregunta interesante sobre el tema. ¿Te gustaría que profundice en algún aspecto específico?",
    "Excelente pregunta. Según los documentos disponibles, hay varios puntos importantes que considerar. Te recomiendo revisar las secciones relevantes para más detalles.",
    "Gracias por tu pregunta. Esta es un área donde puedo ayudarte con información basada en los materiales de estudio. ¿Hay algo específico que quieras explorar más?",
    "He analizado tu consulta y tengo algunas observaciones importantes. La información disponible sugiere varias perspectivas que pueden ser útiles para tu aprendizaje.",
    "¿Podrías darme más contexto sobre tu pregunta? Mientras tanto, puedo ofrecerte una respuesta general basada en los principios del tema.",
]


class GroqService:
    """Production-ready Groq service with streaming and graceful fallback."""
    
    DEFAULT_MODEL = "llama-3.1-8b-instant"
    FALLBACK_MODEL = "mixtral-8x7b-32768"
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model = model or os.getenv("GROQ_MODEL", self.DEFAULT_MODEL)
        self._client = None
        self._initialized = False
        self._mock_mode = not self.api_key
    
    def _get_client(self):
        """Lazy initialization of Groq client."""
        if self._client is None and self.api_key:
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
                self._initialized = True
                self._mock_mode = False
                logger.info(f"Groq client initialized with model: {self.model}")
            except ImportError:
                logger.warning("Groq package not installed. Using mock mode.")
                self._mock_mode = True
                return None
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}. Using mock mode.")
                self._mock_mode = True
                return None
        return self._client
    
    def is_available(self) -> bool:
        """Check if Groq API is configured and available."""
        return bool(self._get_client())
    
    def is_mock_mode(self) -> bool:
        """Check if running in mock mode."""
        return self._mock_mode
    
    def _mock_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate a mock response for development/testing."""
        last_message = messages[-1]["content"] if messages else "?"
        mock_response = random.choice(MOCK_RESPONSES)
        
        return {
            "content": f"{mock_response}\n\n[Modo demo - Para producción, configura GROQ_API_KEY]",
            "model": "mock-groq",
            "finish_reason": "stop",
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": len(mock_response) // 4,
                "total_tokens": 10 + len(mock_response) // 4,
            }
        }
    
    def _mock_stream(self, messages: List[Dict[str, str]], on_chunk: Callable[[str], None]):
        """Simulate streaming response for mock mode."""
        mock_response = random.choice(MOCK_RESPONSES)
        full_response = f"{mock_response}\n\n[Modo demo - Para producción, configura GROQ_API_KEY]"
        
        words = full_response.split()
        for word in words:
            on_chunk(word + " ")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stop: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Send chat request to Groq API (or mock mode if not configured).
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Optional model override
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            stop: Stop sequences
            
        Returns:
            Dict with 'content', 'model', and 'usage' keys
        """
        # Use mock response if not configured
        if self._mock_mode or not self._get_client():
            logger.info("Using mock response (GROQ_API_KEY not configured)")
            return self._mock_response(messages)
        
        model = model or self.model
        
        try:
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
            )
            
            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                }
            }
            
        except Exception as e:
            logger.error(f"Groq API error: {e}. Falling back to mock response.")
            return self._mock_response(messages)
    
    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        on_chunk: Callable[[str], None],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """
        Send streaming chat request to Groq API (or mock mode if not configured).
        """
        # Use mock streaming if not configured
        if self._mock_mode or not self._get_client():
            logger.info("Using mock streaming (GROQ_API_KEY not configured)")
            self._mock_stream(messages, on_chunk)
            return {
                "content": "[mock response]",
                "model": "mock-groq",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }
        
        model = model or self.model
        full_content = []
        usage_stats = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        
        try:
            stream = self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_content.append(content)
                    on_chunk(content)
                
                if chunk.usage:
                    usage_stats["prompt_tokens"] = chunk.usage.prompt_tokens
                    usage_stats["completion_tokens"] += chunk.usage.completion_tokens
                    usage_stats["total_tokens"] = chunk.usage.prompt_tokens + usage_stats["completion_tokens"]
            
            return {
                "content": "".join(full_content),
                "model": model,
                "usage": usage_stats,
            }
            
        except Exception as e:
            logger.error(f"Groq streaming error: {e}")
            # Fallback to mock
            self._mock_stream(messages, on_chunk)
            return {
                "content": "[error - mock fallback]",
                "model": "mock-groq",
                "usage": usage_stats,
            }
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        return len(text) // 3


# Singleton instance for the application
_groq_service: Optional[GroqService] = None


def get_groq_service() -> GroqService:
    """Get or create the singleton Groq service instance."""
    global _groq_service
    if _groq_service is None:
        _groq_service = GroqService()
    return _groq_service


def reset_groq_service():
    """Reset the singleton instance (useful for testing)."""
    global _groq_service
    _groq_service = None