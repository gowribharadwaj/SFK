from pydantic import BaseSettings

class Settings(BaseSettings):
    USE_AZURE: bool = True
    AZURE_OPENAI_ENDPOINT: str = None
    AZURE_OPENAI_KEY: str = None
    AZURE_OPENAI_DEPLOYMENT: str = None
    AZURE_OPENAI_API_VERSION: str = "2024-12-01-preview"

    OPENAI_API_KEY: str = None
    OPENAI_MODEL: str = "gpt-4o"

    USE_REDIS: bool = False
    REDIS_URL: str = "redis://localhost:6379/0"

    PORT: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
