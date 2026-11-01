from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    app_name: str = "CallShield"
    environment: str = "local"

    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-20b"
    groq_fallback_model: str = "openai/gpt-oss-120b"

    groq_timeout_seconds: int = 20
    groq_max_retries: int = 2

    usage_log_path: str = "logs/usage.jsonl"
    input_price_per_million: float | None = None
    output_price_per_million: float | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
