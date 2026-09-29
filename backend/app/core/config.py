from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TechRescue API"
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:3000"]
    database_url: str = "postgresql+psycopg://techrescue:techrescue@localhost:5432/techrescue"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="TECHRESCUE_")


@lru_cache
def get_settings() -> Settings:
    return Settings()
