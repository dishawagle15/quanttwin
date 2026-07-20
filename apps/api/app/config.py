"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the QuantTwin API.

    List-valued environment variables use JSON, for example:
    CORS_ORIGINS='["http://localhost:3000","https://app.example.com"]'
    """

    app_name: str = "QuantTwin API"
    environment: str = "development"
    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-4.1-mini"
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance for the current process."""

    return Settings()
