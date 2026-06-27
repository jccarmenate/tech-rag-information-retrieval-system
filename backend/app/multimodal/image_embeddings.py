from functools import lru_cache
from io import BytesIO

import httpx
from PIL import Image
from sentence_transformers import SentenceTransformer

CLIP_MODEL_NAME = "clip-ViT-B-32"


@lru_cache
def _load_clip(model_name: str) -> SentenceTransformer:
    return SentenceTransformer(model_name)


class ClipEmbeddingModel:
    """CLIP puts images and text in the same vector space, which is what
    lets a plain text query retrieve relevant images (and vice versa) — the
    core requirement of the multimodal module.
    """

    def __init__(self, model_name: str = CLIP_MODEL_NAME) -> None:
        self._model = _load_clip(model_name)

    def encode_text(self, text: str) -> list[float]:
        return self._model.encode(text, normalize_embeddings=True).tolist()

    def encode_image(self, image: Image.Image) -> list[float]:
        return self._model.encode(image, normalize_embeddings=True).tolist()

    def fetch_and_encode_image(self, url: str, timeout: float = 15.0) -> list[float] | None:
        try:
            response = httpx.get(url, timeout=timeout, follow_redirects=True)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content)).convert("RGB")
        except Exception:
            return None
        return self.encode_image(image)
