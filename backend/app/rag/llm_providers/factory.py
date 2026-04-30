from functools import lru_cache

from app.core.config import get_settings
from app.rag.llm_providers.anthropic_provider import AnthropicProvider
from app.rag.llm_providers.base import LLMProvider
from app.rag.llm_providers.ollama_provider import OllamaProvider


def _build_provider() -> LLMProvider:
    settings = get_settings()

    use_anthropic = settings.llm_provider == "anthropic" or (
        settings.llm_provider == "auto" and bool(settings.anthropic_api_key)
    )
    if use_anthropic:
        if not settings.anthropic_api_key:
            raise RuntimeError("LLM_PROVIDER=anthropic requires ANTHROPIC_API_KEY to be set")
        return AnthropicProvider(settings.anthropic_api_key, settings.anthropic_model)

    return OllamaProvider(settings.ollama_base_url, settings.ollama_model)


@lru_cache
def get_llm_provider() -> LLMProvider:
    """Anthropic when ANTHROPIC_API_KEY is set (or LLM_PROVIDER=anthropic), Ollama otherwise.

    This is the single switch a deployment needs: a developer runs a local
    Ollama model with no configuration at all, and anyone deploying the
    system only has to put their Anthropic API key in `.env` — no code or
    RAG pipeline changes required either way.
    """
    return _build_provider()
