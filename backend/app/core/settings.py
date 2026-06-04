from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    APP_NAME: str = "ReDrive Edu"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Server - Railway provides PORT env variable
    SERVER_PORT: int = 8000

    # Database (defaults for local development - use env vars in production)
    DATABASE_URL: str = "sqlite+aiosqlite:///./redrive.db"
    DATABASE_URL_SYNC: str = "sqlite:///./redrive.db"

    # Redis (disabled for local development without Redis)
    REDIS_URL: Optional[str] = None
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # ChromaDB
    CHROMA_USE_CLOUD: bool = False
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

    # CORS - Railway provides Railway's URL in RAILWAY_PUBLIC_DOMAIN
    _railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")
    _railway_url = f"https://{_railway_domain}" if _railway_domain else ""
    _frontend_url = os.getenv("FRONTEND_URL", "")
    
    CORS_ORIGINS: list[str] = [
        "https://*.vercel.app",
        "http://localhost:3000",
        "http://localhost:3001",
        _railway_url,  # Current Railway deployment
        "https://c3po-production-0c24.up.railway.app",  # Production Railway URL
        _frontend_url,  # Frontend URL from env
    ]
    ALLOW_CREDENTIALS: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Railway provides DATABASE_URL - switch from SQLite
        if os.getenv("DATABASE_URL"):
            self.DATABASE_URL = os.getenv("DATABASE_URL")
            if "DATABASE_URL_SYNC" not in os.environ:
                self.DATABASE_URL_SYNC = os.getenv("DATABASE_URL", "").replace("+asyncpg", "").replace("+aiosqlite", "")
        # Railway provides REDIS_URL
        if os.getenv("REDIS_URL"):
            self.REDIS_URL = os.getenv("REDIS_URL")
            self.CELERY_BROKER_URL = os.getenv("REDIS_URL")
            self.CELERY_RESULT_BACKEND = os.getenv("REDIS_URL")
        # Railway provides PORT env variable
        if os.getenv("PORT"):
            self.SERVER_PORT = int(os.getenv("PORT", "8000"))
        # Allow override of SECRET_KEY
        if os.getenv("SECRET_KEY"):
            self.SECRET_KEY = os.getenv("SECRET_KEY")
        # Allow override of CORS_ORIGINS (comma-separated)
        if os.getenv("CORS_ORIGINS"):
            self.CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",")]
        # Railway sets ENVIRONMENT
        if os.getenv("ENVIRONMENT"):
            self.DEBUG = os.getenv("ENVIRONMENT", "").lower() == "development"


settings = Settings()

