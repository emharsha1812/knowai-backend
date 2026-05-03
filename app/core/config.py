from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Literal
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    APP_NAME: str = "KnowAI"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: Literal["development", "production", "test"] = "production"
    DEBUG: bool = False

    # Security — must be set via env var in production
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_strong(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://knowai:knowai@localhost:5432/knowai"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_database_url(cls, v: str) -> str:
        # Railway provides postgresql:// but asyncpg needs postgresql+asyncpg://
        if isinstance(v, str) and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS — plain string to avoid pydantic-settings auto JSON decoding
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v):
        if isinstance(v, str):
            value = v.strip().lower()
            if value in {"1", "true", "yes", "on", "debug", "development"}:
                return True
            if value in {"0", "false", "no", "off", "release", "production", ""}:
                return False
        return v

    @property
    def allowed_origins_list(self) -> list[str]:
        value = self.ALLOWED_ORIGINS.strip()
        if not value:
            return ["http://localhost:3000"]
        if value.startswith("["):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        return [o.strip() for o in value.split(",") if o.strip()]

    # Code execution sandbox
    EXECUTION_TIMEOUT_SECONDS: int = 10
    EXECUTION_MEMORY_MB: int = 128

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"


settings = Settings()
