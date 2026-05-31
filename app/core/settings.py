from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    APP_NAME: str = "C3PO - AI Tutor"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ChromaDB
    CHROMA_HOST: Optional[str] = "localhost"
    CHROMA_PORT: int = 8000

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    # Logging
    LOG_LEVEL: str = "INFO"


settings = Settings()
