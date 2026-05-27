# ReDrive Edu - Backend
# AI-native educational tutoring platform with RAG

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    APP_NAME: str = "ReDrive Edu"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/redrive_edu"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://postgres:postgres@postgres:5432/redrive_edu"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"

    # ChromaDB
    CHROMA_USE_CLOUD: bool = True
    CHROMA_CLOUD_API_KEY: Optional[str] = None
    CHROMA_CLOUD_HOST: str = "api.trychroma.com"
    CHROMA_CLOUD_PORT: int = 443
    CHROMA_CLOUD_ENABLE_SSL: bool = True
    CHROMA_CLOUD_TENANT: Optional[str] = None
    CHROMA_CLOUD_DATABASE: Optional[str] = None
    CHROMA_PERSIST_DIR: str = "./chroma_data"

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_EMBEDDING_DIM: int = 1536

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Document Processing
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: list[str] = [".pdf", ".docx", ".txt", ".md"]
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    ALLOW_CREDENTIALS: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"


settings = Settings()