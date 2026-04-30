from anthropic import Anthropic

from app.rag.llm_providers.base import LLMProvider


class AnthropicProvider(LLMProvider):
    """Generates text via the Anthropic Messages API."""

    def __init__(self, api_key: str, model: str, max_tokens: int = 1024) -> None:
        self.model = model
        self.max_tokens = max_tokens
        self._client = Anthropic(api_key=api_key)

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        message = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system or "",
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in message.content if block.type == "text").strip()
