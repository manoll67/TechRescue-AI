import json
from functools import lru_cache
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TechRescue API"
    api_prefix: str = "/api/v1"
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]
    database_url: str = "postgresql+psycopg://techrescue:techrescue@localhost:5432/techrescue"
    session_ttl_hours: int = 24 * 7
    login_attempt_limit: int = 10
    login_attempt_window_seconds: int = 300

    model_config = SettingsConfigDict(env_file=".env", env_prefix="TECHRESCUE_")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        text = value.strip()
        if text.startswith("["):
            return json.loads(text)
        return [origin.strip() for origin in text.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
