"""
Application configuration using pydantic-settings.

All settings are loaded from environment variables with sensible defaults
for local development. In production, override via .env file or environment.
"""

from functools import lru_cache
from typing import ClassVar

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application settings.

    Attributes:
        APP_NAME: Display name of the application.
        APP_VERSION: Semantic version string.
        DEBUG: Enable debug mode (extra logging, detailed errors).
        API_V1_PREFIX: URL prefix for all v1 API routes.
        DATABASE_URL: Async PostgreSQL connection string.
        DATABASE_ECHO: Echo SQL statements to stdout (for debugging).
        DATABASE_POOL_SIZE: Number of persistent connections in the pool.
        DATABASE_MAX_OVERFLOW: Max additional connections beyond pool_size.
        JWT_SECRET_KEY: HMAC secret for signing JWT tokens (override in prod!).
        JWT_ALGORITHM: Algorithm used for JWT encoding/decoding.
        ACCESS_TOKEN_EXPIRE_MINUTES: Lifetime of an access token.
        REFRESH_TOKEN_EXPIRE_DAYS: Lifetime of a refresh token.
        CORS_ORIGINS: Comma-separated list of allowed CORS origins.
        RATE_LIMIT_PER_MINUTE: Max requests per minute for rate-limited endpoints.
        UPLOAD_DIR: Directory where uploaded documents are stored.
        MAX_UPLOAD_SIZE_MB: Maximum file upload size in megabytes.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────
    APP_NAME: str = "ResearchMind AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # ── Database ─────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/researchmind"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # ── JWT Authentication ───────────────────────────────────────────
    JWT_SECRET_KEY: str = "CHANGE-ME-IN-PRODUCTION-USE-A-REAL-SECRET-KEY-AT-LEAST-32-CHARS"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── CORS ─────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]

    # ── Rate Limiting ────────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 100

    # ── File Upload ──────────────────────────────────────────────────
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 50

    # ── Vector DB & LLM Settings (Phase 3) ──────────────────────────
    CHROMA_PERSIST_DIR: str = "chroma_data"
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str | None = None
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # ── Allowed file extensions for document upload ──────────────────
    ALLOWED_EXTENSIONS: ClassVar[set[str]] = {
        ".pdf", ".docx", ".doc", ".txt", ".md", ".tex",
    }


    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from a comma-separated string or a list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def max_upload_size_bytes(self) -> int:
        """Return the maximum upload size in bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a cached singleton of the application settings.

    Uses ``lru_cache`` so the ``.env`` file is read only once per process.
    """
    return Settings()
