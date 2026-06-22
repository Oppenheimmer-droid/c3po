"""
OpenAI AI Service - Production-ready integration with GPT models.
Provides embeddings, chat completions, and streaming support.
"""

import os
import logging
from typing import Optional, Callable, List, Dict, Any

logger = logging.getLogger(__name__)


class OpenAIService:
    """Production-ready OpenAI service for embeddings and chat."""
    
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
    
    def _get_client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None and self.api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
                logger.info(f"OpenAI client initialized with model: {self.model}")
            except ImportError:
                logger.error("OpenAI package not installed. Run: pip install openai")
                return None
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                return None
        return self._client
    
    def is_available(self) -> bool:
        """Check if OpenAI API is configured."""
        return bool(self._get_client())
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """
        Send chat request to OpenAI API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Optional model override
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dict with 'content', 'model', and 'usage' keys
        """
        client = self._get_client()
        
        if client is None:
            raise RuntimeError(
                "OpenAI API not configured. Set OPENAI_API_KEY environment variable."
            )
        
        model = model or self.model
        
        try:
            response = client.chat.completions.create(
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
            logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"OpenAI API failed: {e}")
    
    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        on_chunk: Callable[[str], None],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """
        Send streaming chat request to OpenAI API.
        """
        client = self._get_client()
        
        if client is None:
            raise RuntimeError("OpenAI API not configured")
        
        model = model or self.model
        full_content = []
        usage_stats = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        
        try:
            stream = client.chat.completions.create(
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
            raise RuntimeError(f"OpenAI streaming failed: {e}")
    
    def create_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None,
    ) -> List[List[float]]:
        """
        Create embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            model: Optional embedding model override
            
        Returns:
            List of embedding vectors (each is a list of floats)
        """
        client = self._get_client()
        
        if client is None:
            raise RuntimeError("OpenAI API not configured")
        
        model = model or self.embedding_model
        
        try:
            response = client.embeddings.create(
                model=model,
                input=texts,
            )
            
            return [item.embedding for item in response.data]
            
        except Exception as e:
            logger.error(f"OpenAI embeddings error: {e}")
            raise RuntimeError(f"OpenAI embeddings failed: {e}")
    
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
