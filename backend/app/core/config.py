# app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from functools import lru_cache
from pathlib import Path

class Settings(BaseSettings):
    # Project Info
    API_V1_STR: str = "/v1"
    PROJECT_NAME: str = "Diagnosis Application"
    ENV: str = "development"

    # Static files
    STATIC_DIR: str = "static"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # Database settings from .env
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    DB_SCHEMA: str = "public"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_ECHO: bool = False

    # JWT settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Cookie settings
    COOKIE_DOMAIN: str = "localhost"
    COOKIE_SECURE: bool = False  # Set to True in production with HTTPS
    COOKIE_SAMESITE: str = "lax"

    # Compose the full DATABASE URL
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(env_file=Path(__file__).parent.parent.parent / ".env", extra="ignore", case_sensitive=True)
    print(f"Loading settings from {model_config}")

@lru_cache
def get_settings() -> Settings:
    return Settings() # type: ignore

settings = get_settings()
