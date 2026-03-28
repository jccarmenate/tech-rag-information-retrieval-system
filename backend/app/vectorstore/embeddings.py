from functools import lru_cache

from sentence_transformers import SentenceTransformer

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache
def _load_model(model_name: str) -> SentenceTransformer:
    return SentenceTransformer(model_name)


class EmbeddingModel:
    """Thin wrapper so the rest of the codebase never touches SentenceTransformer directly."""

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME) -> None:
        self.model_name = model_name
        self._model = _load_model(model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = self._model.encode(texts, normalize_embeddings=True)
        return vectors.tolist()

    def encode_one(self, text: str) -> list[float]:
        return self.encode([text])[0]
