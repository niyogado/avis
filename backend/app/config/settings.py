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
    # S3 / object storage settings (optional)
    S3_ENABLED: bool = False
    S3_BUCKET: str = ""
    S3_REGION: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""

    # Upload validation
    MAX_UPLOAD_SIZE: int = 5_000_000  # bytes (5 MB)
    ALLOWED_UPLOAD_TYPES: list[str] = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()