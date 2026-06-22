"""
Application settings - Production-ready configuration.
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration with environment variable support."""
    
    # ── Application ──────────────────────────────────────────
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str = "dev-secret-change-in-production-min-32-chars"
    PORT: int = 8000

    # ── Database ─────────────────────────────────────────────
    DATABASE_URL: str = ""
    DATABASE_URL_SYNC: str = ""

    # ── CORS ─────────────────────────────────────────────────
    CORS_ORIGINS: str = "*"
    ALLOW_CREDENTIALS: bool = True

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # ── AI Provider Selection ────────────────────────────────
    # Options: "groq" (recommended - faster, cheaper) or "openai"
    AI_PROVIDER: str = "groq"

    # ── Groq Configuration ────────────────────────────────────
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    @property
    def groq_available(self) -> bool:
        """Check if Groq API is configured."""
        return bool(self.GROQ_API_KEY)

    # ── OpenAI Configuration ──────────────────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_EMBEDDING_DIM: int = 1536

    @property
    def openai_available(self) -> bool:
        """Check if OpenAI API is configured."""
        return bool(self.OPENAI_API_KEY)

    # ── JWT Configuration ────────────────────────────────────
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # ── Document Processing ────────────────────────────────────
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_FILE_SIZE_MB: int = 50

    # ── Redis Configuration ──────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ── ChromaDB Configuration ────────────────────────────────
    CHROMA_USE_CLOUD: bool = False
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    CHROMA_PERSIST_DIR: str = "./chroma_data"

    @property
    def chroma_available(self) -> bool:
        """Check if ChromaDB is configured."""
        return bool(self.CHROMA_HOST)

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
