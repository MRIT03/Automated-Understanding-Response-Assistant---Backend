from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Fire Dispatcher Backend"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    debug: bool = True
    secret_key: str = "change-me"
    auto_create_tables: bool = True

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/fire_dispatch"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    chroma_collection_name: str = "dispatcher_knowledge"
    chroma_persist_directory: str = "./chroma_store"

    allow_origins: List[str] = Field(default_factory=lambda: ["*"])


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
