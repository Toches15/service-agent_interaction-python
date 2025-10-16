"""
Application configuration management.

This module provides centralized configuration management using pydantic-settings
for type-safe environment variable handling and validation.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    This class defines all configuration options for the application,
    with sensible defaults and automatic environment variable loading.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    # Application settings
    app_name: str = Field(default="FastAPI Template", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: Literal["development", "staging", "production"] = Field(
        default="development", description="Environment name"
    )

    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, ge=1, le=65535, description="Server port")
    reload: bool = Field(default=True, description="Auto-reload on code changes")

    # Security settings
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        min_length=32,
        description="Secret key for cryptographic operations",
    )
    allowed_hosts: list[str] = Field(default=["*"], description="Allowed hosts for CORS")

    # Logging settings
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )
    log_format: Literal["text", "json"] = Field(
        default="text", description="Log format (text for development, json for production)"
    )

    # API settings
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")
    docs_url: str | None = Field(default="/docs", description="Swagger UI URL")
    redoc_url: str | None = Field(default="/redoc", description="ReDoc URL")

    # Database settings
    use_database: bool = Field(default=False, description="Enable database support")
    database_url: str | None = Field(default=None, description="Database connection URL (if not set, uses SQLite)")

    # Add your project-specific settings here:
    # redis_url: str | None = Field(default=None, description="Redis connection URL")
    # openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    # smtp_host: str | None = Field(default=None, description="SMTP server host")
    # upload_dir: str = Field(default="uploads", description="Upload directory path")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment setting."""
        if v not in ["development", "staging", "production"]:
            raise ValueError("Environment must be development, staging, or production")
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.

    This function returns a cached instance of the Settings class,
    ensuring configuration is loaded only once per application lifecycle.

    Returns:
        Settings: Application configuration instance.
    """
    return Settings()


# Global settings instance
settings = get_settings()
