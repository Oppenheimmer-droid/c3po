from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "production"

    DATABASE_URL: str
    ASYNC_DATABASE_URL: str

    CHROMA_HOST: str
    CHROMA_PORT: int = 8000

    OPENAI_API_KEY: str

    JWT_SECRET_KEY: str = "supersecret"
    JWT_REFRESH_SECRET_KEY: str = "supersecret"

    CORS_ORIGINS: list[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
