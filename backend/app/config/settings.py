from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "AVIS Core Backend"

    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:avis_dbpass@localhost:5432/avis_db"
    )

    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000"
    ]
    UPLOAD_DIR: str = "uploads"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()