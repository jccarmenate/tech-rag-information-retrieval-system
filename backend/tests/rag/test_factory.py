import pytest
from app.core.config import Settings
from app.rag.llm_providers import factory
from app.rag.llm_providers.anthropic_provider import AnthropicProvider
from app.rag.llm_providers.ollama_provider import OllamaProvider


def _settings(**overrides) -> Settings:
    return Settings(**overrides)


def test_auto_mode_uses_ollama_without_api_key(monkeypatch):
    monkeypatch.setattr(factory, "get_settings", lambda: _settings(llm_provider="auto"))
    assert isinstance(factory._build_provider(), OllamaProvider)


def test_auto_mode_uses_anthropic_when_api_key_present(monkeypatch):
    monkeypatch.setattr(
        factory, "get_settings", lambda: _settings(llm_provider="auto", anthropic_api_key="sk-x")
    )
    assert isinstance(factory._build_provider(), AnthropicProvider)


def test_explicit_ollama_ignores_api_key(monkeypatch):
    monkeypatch.setattr(
        factory,
        "get_settings",
        lambda: _settings(llm_provider="ollama", anthropic_api_key="sk-x"),
    )
    assert isinstance(factory._build_provider(), OllamaProvider)


def test_explicit_anthropic_without_key_raises(monkeypatch):
    monkeypatch.setattr(
        factory, "get_settings", lambda: _settings(llm_provider="anthropic", anthropic_api_key=None)
    )
    with pytest.raises(RuntimeError):
        factory._build_provider()
