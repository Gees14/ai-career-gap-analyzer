from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "AI Career Gap Analyzer"
    app_version: str = "1.0.0"
    debug: bool = False

    # LLM (optional — system works fully without this)
    openai_api_key: Optional[str] = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    # Embedding model (local, no API key required)
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    embedding_batch_size: int = 32

    # Upload limits
    max_upload_size_mb: int = 10

    # Scoring weights per category (must sum to 1.0)
    score_weight_exact: float = 0.6
    score_weight_semantic: float = 0.4

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
