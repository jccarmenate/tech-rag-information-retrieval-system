import httpx

from app.rag.llm_providers.base import LLMProvider


class OllamaProvider(LLMProvider):
    """Generates text via a locally running Ollama server (`ollama serve`)."""

    def __init__(self, base_url: str, model: str, timeout_seconds: float = 120.0) -> None:
        self.model = model
        self._client = httpx.Client(base_url=base_url, timeout=timeout_seconds)

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        response = self._client.post(
            "/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "system": system or "",
                "stream": False,
            },
        )
        response.raise_for_status()
        return response.json()["response"].strip()
