from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NightBreach"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True

    api_prefix: str = "/api/v1"

    database_url: str = (
        "postgresql+asyncpg://nightbreach:nightbreach@localhost:5432/nightbreach"
    )

    jwt_secret_key: str = "development-only-change-me-use-a-longer-key"
    jwt_algorithm: str = "HS256"
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
