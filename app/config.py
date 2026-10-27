
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    app_name: str = "CallShield"
    environment: str = "local"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    gemini_fallback_model: str = "gemini-3.1-flash-lite"

    gemini_timeout_seconds: int = 20
    gemini_max_retries: int = 2


@lru_cache
def get_settings() -> Settings:
    return Settings()

