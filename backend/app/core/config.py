from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "CodeRadar"
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:5173"]
    database_url: str = "sqlite:///./data/coderadar.db"
    acquisition_interval_hours: float = 6.0
    acquisition_limit_per_source: int = 20
    github_token: str | None = None
    chroma_persist_dir: str = "data/chroma"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache
def get_settings() -> Settings:
    return Settings()
