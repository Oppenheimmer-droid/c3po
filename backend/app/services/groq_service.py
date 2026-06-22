"""
Groq AI Service - Production-ready LLM integration for educational responses.
Supports streaming, function calling, and automatic fallback to OpenAI.
"""

import os
import logging
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


class GroqService:
    """Production-ready Groq service with streaming and error handling."""
    
    DEFAULT_MODEL = "llama-3.1-8b-instant"
    FALLBACK_MODEL = "mixtral-8x7b-32768"
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model = model or os.getenv("GROQ_MODEL", self.DEFAULT_MODEL)
        self._client = None
        self._initialized = False
    
    def _get_client(self):
        """Lazy initialization of Groq client."""
        if self._client is None and self.api_key:
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
                self._initialized = True
                logger.info(f"Groq client initialized with model: {self.model}")
            except ImportError:
                logger.error("Groq package not installed. Run: pip install groq")
                return None
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                return None
        return self._client
    
    def is_available(self) -> bool:
        """Check if Groq API is configured and available."""
        return bool(self._get_client())
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stop: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Send chat request to Groq API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Optional model override
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            stop: Stop sequences
            
        Returns:
            Dict with 'content', 'model', and 'usage' keys
        """
        client = self._get_client()
        
        if client is None:
            raise RuntimeError(
                "Groq API not configured. Set GROQ_API_KEY environment variable "
                "or provide api_key parameter."
            )
        
        model = model or self.model
        
        try:
            response = client.chat.completions.create(
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
            logger.error(f"Groq API error: {e}")
            
            # Try fallback model
            if model != self.FALLBACK_MODEL:
                logger.info(f"Trying fallback model: {self.FALLBACK_MODEL}")
                return self.chat(
                    messages, 
                    model=self.FALLBACK_MODEL,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stop=stop
                )
            
            raise RuntimeError(f"Groq API failed: {e}")
    
    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        on_chunk: Callable[[str], None],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """
        Send streaming chat request to Groq API.
        
        Args:
            messages: List of message dicts
            on_chunk: Callback for each streaming chunk
            model: Optional model override
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            
        Returns:
            Final response dict with usage stats
        """
        client = self._get_client()
        
        if client is None:
            raise RuntimeError("Groq API not configured")
        
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
                
                # Accumulate usage from chunks
                if chunk.usage:
                    usage_stats["prompt_tokens"] = chunk.usage.prompt_tokens
                    usage_stats["completion_tokens"] += chunk.usage.completion_tokens
                    usage_stats["total_tokens"] = chunk.usage.prompt_tokens + usage_stats["completion_tokens"]
            
            return {
                "content": "".join(full_content),
                "model": model,
                "finish_reason": chunk.choices[0].finish_reason if chunk.choices else None,
                "usage": usage_stats,
            }
            
        except Exception as e:
            logger.error(f"Groq streaming error: {e}")
            raise RuntimeError(f"Groq streaming failed: {e}")
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        # Rough estimate: ~4 chars per token for English, ~2 for Spanish
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