from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str = "dev-secret-change-in-production-min-32-chars"

    # ── Base de datos ─────────────────────────────────────────
    DATABASE_URL: str = ""
    DATABASE_URL_SYNC: str = ""

    # ── CORS ──────────────────────────────────────────────────
    # Railway almacena este valor como CSV separado por comas.
    # El property cors_origins lo parsea en lista para CORSMiddleware.
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,https://*.vercel.app"
    ALLOW_CREDENTIALS: bool = True

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    # ── OpenAI ────────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_EMBEDDING_DIM: int = 1536
    OPENAI_MOCK: bool = False

    # ── Groq ──────────────────────────────────────────────────
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GROQ_MOCK: bool = False

    # ── AI Provider Selection ─────────────────────────────────
    # Options: "groq", "openai"
    AI_PROVIDER: str = "groq"

    # ── JWT ──────────────────────────────────────────────
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # ── Document Processing ─────────────────────────────
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_FILE_SIZE_MB: int = 50

    # ── Redis ─────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ── ChromaDB ──────────────────────────────────────────────
    CHROMA_USE_CLOUD: bool = False
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    CHROMA_PERSIST_DIR: str = "./chroma_data"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
