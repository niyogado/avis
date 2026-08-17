from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AVIS Core Backend"

    DATABASE_URL: str = (
        "postgresql://user:password@localhost:5432/avis_db"
    )

    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    BACKEND_CORS_ORIGINS: list[AnyUrl] = [
        "http://localhost:3000"
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()