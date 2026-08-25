from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Tech RAG Information Retrieval System"
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:5173"]
    database_url: str = "sqlite:///./data/app.db"
    acquisition_interval_hours: float = 6.0
    acquisition_limit_per_source: int = 20
    github_token: str | None = None
    chroma_persist_dir: str = "data/chroma"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"

    # RAG / LLM provider selection. "auto" uses Anthropic when an API key is
    # configured and falls back to a local Ollama model otherwise, so a
    # developer can iterate offline while a deployment just sets the key.
    llm_provider: str = "auto"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-5"


@lru_cache
def get_settings() -> Settings:
    return Settings()
