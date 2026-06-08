from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str = "dev-secret-change-in-production-min-32-chars"

    # ── Base de datos ─────────────────────────────────────
    DATABASE_URL: str = ""
    DATABASE_URL_SYNC: str = ""

    # ── CORS ─────────────────────────────────────────────
    # Railway almacena este valor como string CSV separado por comas.
    # El property cors_origins lo convierte en lista para CORSMiddleware.
    CORS_ORIGINS: str = "http://localhost:3000"
    ALLOW_CREDENTIALS: bool = True

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # ── OpenAI ────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_MOCK: bool = False

    # ── Redis ─────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ── ChromaDB ──────────────────────────────────────────
    CHROMA_USE_CLOUD: bool = False
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    CHROMA_PERSIST_DIR: str = "./chroma_data"

    class Config:
        env_file = ".env"
        extra = "ignore"   # ignora variables de Railway que no estén definidas aquí


settings = Settings()
