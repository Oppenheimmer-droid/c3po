"""
OpenAI AI Service - Production-ready integration with GPT models.
Provides embeddings, chat completions, and streaming support.
"""

import os
import logging
import random
from typing import Optional, Callable, List, Dict, Any

logger = logging.getLogger(__name__)


# Sample responses for mock mode
MOCK_RESPONSES = [
    "He procesado tu pregunta y puedo ofrecerte una respuesta basada en los principios generales del tema.",
    "Excelente consulta. Te proporciono información general que puede ayudarte con tu aprendizaje.",
    "Gracias por tu mensaje. Esta es una pregunta interesante que puedo abordar con información general.",
]


class OpenAIService:
    """Production-ready OpenAI service with graceful fallback."""
    
    DEFAULT_MODEL = "gpt-4o-mini"
    EMBEDDING_MODEL = "text-embedding-3-small"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        embedding_model: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model or os.getenv("OPENAI_MODEL", self.DEFAULT_MODEL)
        self.embedding_model = embedding_model or os.getenv(
            "OPENAI_EMBEDDING_MODEL", self.EMBEDDING_MODEL
        )
        self._client = None
        self._mock_mode = not self.api_key
    
    def _get_client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None and self.api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
                self._mock_mode = False
                logger.info(f"OpenAI client initialized with model: {self.model}")
            except ImportError:
                logger.warning("OpenAI package not installed. Using mock mode.")
                self._mock_mode = True
                return None
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}. Using mock mode.")
                self._mock_mode = True
                return None
        return self._client
    
    def is_available(self) -> bool:
        """Check if OpenAI API is configured."""
        return bool(self._get_client())
    
    def is_mock_mode(self) -> bool:
        """Check if running in mock mode."""
        return self._mock_mode
    
    def _mock_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate a mock response for development/testing."""
        mock_response = random.choice(MOCK_RESPONSES)
        
        return {
            "content": f"{mock_response}\n\n[Modo demo - Para producción, configura OPENAI_API_KEY]",
            "model": "mock-gpt-4o-mini",
            "finish_reason": "stop",
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": len(mock_response) // 4,
                "total_tokens": 10 + len(mock_response) // 4,
            }
        }
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """
        Send chat request to OpenAI API (or mock mode if not configured).
        """
        if self._mock_mode or not self._get_client():
            logger.info("Using mock response (OPENAI_API_KEY not configured)")
            return self._mock_response(messages)
        
        model = model or self.model
        
        try:
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
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
            logger.error(f"OpenAI API error: {e}. Falling back to mock.")
            return self._mock_response(messages)
    
    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        on_chunk: Callable[[str], None],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """Send streaming chat request to OpenAI API."""
        if self._mock_mode or not self._get_client():
            logger.info("Using mock streaming (OPENAI_API_KEY not configured)")
            mock_response = random.choice(MOCK_RESPONSES)
            for word in mock_response.split():
                on_chunk(word + " ")
            return {
                "content": "[mock]",
                "model": "mock-gpt-4o-mini",
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
                    usage_stats["total_tokens"] = chunk.usage.total_tokens
            
            return {
                "content": "".join(full_content),
                "model": model,
                "usage": usage_stats,
            }
            
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            return self._mock_response(messages)
    
    def create_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None,
    ) -> List[List[float]]:
        """Create embeddings for a list of texts."""
        if self._mock_mode or not self._get_client():
            logger.info("Using mock embeddings (OPENAI_API_KEY not configured)")
            dim = self.get_embedding_dim()
            return [[random.uniform(-1, 1) for _ in range(dim)] for _ in texts]
        
        model = model or self.embedding_model
        
        try:
            response = self._client.embeddings.create(
                model=model,
                input=texts,
            )
            return [item.embedding for item in response.data]
            
        except Exception as e:
            logger.error(f"OpenAI embeddings error: {e}")
            dim = self.get_embedding_dim()
            return [[random.uniform(-1, 1) for _ in range(dim)] for _ in texts]
    
    def get_embedding_dim(self) -> int:
        """Get embedding dimension based on model."""
        dims = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1538,
        }
        return dims.get(self.embedding_model, 1536)


# Singleton instance
_openai_service: Optional[OpenAIService] = None


def get_openai_service() -> OpenAIService:
    """Get or create the singleton OpenAI service instance."""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service


def reset_openai_service():
    """Reset the singleton instance."""
    global _openai_service
    _openai_service = None
