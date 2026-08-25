from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """A swappable text-generation backend for the RAG pipeline.

    Keeping this interface tiny (one method) is what lets this system run
    entirely offline against a local Ollama model during development while
    a deployment only has to set ANTHROPIC_API_KEY to switch to Claude,
    without touching any RAG orchestration code.
    """

    @abstractmethod
    def generate(self, prompt: str, *, system: str | None = None) -> str:
        raise NotImplementedError
