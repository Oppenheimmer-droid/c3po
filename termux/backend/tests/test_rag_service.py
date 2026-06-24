"""
Tests for RAG Service.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock


class TestRAGService:
    """Test cases for RAG Service."""

    def test_rag_service_initialization(self):
        """Test RAG service can be initialized."""
        from app.services.rag_service import RAGService, AIProvider
        
        service = RAGService(db=None, provider=AIProvider.GROQ)
        assert service.provider == AIProvider.GROQ
        assert service.db is None

    def test_rag_service_with_openai_provider(self):
        """Test RAG service with OpenAI provider."""
        from app.services.rag_service import RAGService, AIProvider
        
        service = RAGService(db=None, provider=AIProvider.OPENAI)
        assert service.provider == AIProvider.OPENAI

    def test_build_messages_without_context(self):
        """Test building messages without context."""
        from app.services.rag_service import RAGService
        
        service = RAGService(db=None)
        messages = service._build_messages("What is Python?", [])
        
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert "What is Python?" in messages[1]["content"]

    def test_build_messages_with_context(self):
        """Test building messages with context chunks."""
        from app.services.rag_service import RAGService
        
        service = RAGService(db=None)
        context_chunks = [
            {"content": "Python is a programming language.", "metadata": {"source": "doc1"}},
            {"content": "It was created by Guido van Rossum.", "metadata": {"source": "doc2"}},
        ]
        messages = service._build_messages("Tell me about Python", context_chunks)
        
        assert len(messages) == 2
        assert "Python is a programming language" in messages[1]["content"]
        assert "doc1" in messages[1]["content"]

    def test_fallback_response(self):
        """Test fallback response generation."""
        from app.services.rag_service import RAGService
        
        service = RAGService(db=None)
        response = service._fallback_response("test query", "API unavailable", 0.5)
        
        assert "no esta disponible" in response["answer"]
        assert response["sources"] == []
        assert response["citations"] == []
        assert response["tokens_used"] == 0
        assert response["model"] == "fallback"
        assert response["provider"] == "none"


class TestGroqService:
    """Test cases for Groq Service."""

    def test_groq_service_initialization(self):
        """Test Groq service can be initialized without API key."""
        from app.services.groq_service import GroqService
        
        service = GroqService(api_key="")
        assert service.api_key == ""
        assert service._client is None

    def test_groq_service_with_api_key(self):
        """Test Groq service with mock API key."""
        from app.services.groq_service import GroqService
        
        service = GroqService(api_key="test-key")
        assert service.api_key == "test-key"
        assert service.model == "llama-3.1-8b-instant"

    def test_groq_is_available_false(self):
        """Test is_available returns False without API key."""
        from app.services.groq_service import GroqService
        
        service = GroqService(api_key="")
        assert service.is_available() is False

    def test_groq_count_tokens(self):
        """Test token counting approximation."""
        from app.services.groq_service import GroqService
        
        service = GroqService()
        tokens = service.count_tokens("Hello world")
        assert tokens > 0


class TestOpenAIService:
    """Test cases for OpenAI Service."""

    def test_openai_service_initialization(self):
        """Test OpenAI service can be initialized."""
        import os
        from app.services.openai_service import OpenAIService
        
        # Clear env var to ensure consistent test
        original_key = os.environ.pop('OPENAI_API_KEY', None)
        
        try:
            # Test with explicit empty key
            service = OpenAIService(api_key="")
            assert service.api_key == ""
            # With empty key, should be mock mode
            assert service._mock_mode is True
            
            # Test default models work
            service2 = OpenAIService()
            assert service2.model == "gpt-4o-mini"
            assert service2.embedding_model == "text-embedding-3-small"
        finally:
            # Restore original env var
            if original_key:
                os.environ['OPENAI_API_KEY'] = original_key

    def test_openai_is_available_false(self):
        """Test is_available returns False without API key."""
        import os
        from app.services.openai_service import OpenAIService
        
        # Clear env var
        original_key = os.environ.pop('OPENAI_API_KEY', None)
        try:
            service = OpenAIService(api_key="")
            assert service.is_available() is False
        finally:
            if original_key:
                os.environ['OPENAI_API_KEY'] = original_key

    def test_openai_default_models(self):
        """Test default model configuration."""
        from app.services.openai_service import OpenAIService
        
        service = OpenAIService()
        assert service.model == "gpt-4o-mini"
        assert service.embedding_model == "text-embedding-3-small"


class TestVectorStore:
    """Test cases for Vector Store."""

    def test_vector_store_initialization(self):
        """Test Vector store can be initialized."""
        from app.rag.vector_store import VectorStore
        
        store = VectorStore()
        assert store.host == "localhost"
        assert store.port == 8000

    def test_vector_store_custom_config(self):
        """Test Vector store with custom configuration."""
        from app.rag.vector_store import VectorStore
        
        store = VectorStore(host="chroma.example.com", port=8080)
        assert store.host == "chroma.example.com"
        assert store.port == 8080

    def test_retrieval_pipeline_no_tenant(self):
        """Test retrieval pipeline returns empty when no tenant."""
        from app.rag.vector_store import retrieval_pipeline
        
        result = retrieval_pipeline(query="test", tenant_id=None)
        assert result["chunks"] == []
        assert "No tenant_id" in result["debug"]

    def test_retrieval_pipeline_empty_query(self):
        """Test retrieval pipeline with empty query."""
        from app.rag.vector_store import retrieval_pipeline
        
        result = retrieval_pipeline(query="", tenant_id="test-tenant")
        # Should return empty chunks or handle gracefully
        assert "chunks" in result


class TestSettings:
    """Test cases for application settings."""

    def test_settings_defaults(self):
        """Test default settings values."""
        from app.core.settings import Settings
        
        # Create instance with test values
        settings = Settings(
            ENVIRONMENT="test",
            AI_PROVIDER="groq",
        )
        
        assert settings.ENVIRONMENT == "test"
        assert settings.AI_PROVIDER == "groq"

    def test_cors_origins_wildcard(self):
        """Test CORS origins with wildcard."""
        from app.core.settings import Settings
        
        settings = Settings(CORS_ORIGINS="*")
        origins = settings.cors_origins
        assert origins == ["*"]

    def test_cors_origins_list(self):
        """Test CORS origins with multiple origins."""
        from app.core.settings import Settings
        
        settings = Settings(CORS_ORIGINS="http://localhost:3000,http://localhost:3001")
        origins = settings.cors_origins
        assert len(origins) == 2
        assert "http://localhost:3000" in origins

    def test_groq_available_property(self):
        """Test groq_available property."""
        from app.core.settings import Settings
        
        settings = Settings(GROQ_API_KEY="")
        assert settings.groq_available is False
        
        settings = Settings(GROQ_API_KEY="test-key")
        assert settings.groq_available is True

    def test_openai_available_property(self):
        """Test openai_available property."""
        from app.core.settings import Settings
        
        settings = Settings(OPENAI_API_KEY="")
        assert settings.openai_available is False
        
        settings = Settings(OPENAI_API_KEY="test-key")
        assert settings.openai_available is True
