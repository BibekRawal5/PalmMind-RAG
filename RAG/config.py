from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    DATABASE_URL: str
    QDRANT_URL: str
    QDRANT_API: str
    REDIS_URL: str
    COLLECTION_NAME: str
    EMBED_MODEL: str
    GEMINI_API_KEY: str
    GEMINI_MODEL: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str
    SMTP_FROM: EmailStr | str

settings = Settings()
