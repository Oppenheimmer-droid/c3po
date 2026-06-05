from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    OPENAI_MOCK: bool = True  # Siempre mock por defecto

settings = Settings()
