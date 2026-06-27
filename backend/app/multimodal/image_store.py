from dataclasses import dataclass

import chromadb

from app.core.config import get_settings
from app.multimodal.image_embeddings import ClipEmbeddingModel

COLLECTION_NAME = "images"


@dataclass
class ImageHit:
    doc_id: str
    image_url: str
    similarity: float


class ImageStore:
    """A second, independent Chroma collection (same persist directory as the
    text vector store) holding one CLIP embedding per document image.
    """

    def __init__(
        self, persist_dir: str | None = None, embedding_model: ClipEmbeddingModel | None = None
    ) -> None:
        settings = get_settings()
        self._client = chromadb.PersistentClient(path=persist_dir or settings.chroma_persist_dir)
        self._collection = self._client.get_or_create_collection(
            COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )
        self._embedder = embedding_model or ClipEmbeddingModel()

    def upsert_image(self, doc_id: str, image_url: str) -> bool:
        vector = self._embedder.fetch_and_encode_image(image_url)
        if vector is None:
            return False
        self._collection.upsert(
            ids=[doc_id], embeddings=[vector], metadatas=[{"image_url": image_url}]
        )
        return True

    def query_by_text(self, text: str, top_k: int = 10) -> list[ImageHit]:
        if self._collection.count() == 0:
            return []
        vector = self._embedder.encode_text(text)
        result = self._collection.query(query_embeddings=[vector], n_results=top_k)
        hits = []
        for doc_id, metadata, distance in zip(
            result["ids"][0], result["metadatas"][0], result["distances"][0], strict=True
        ):
            hits.append(
                ImageHit(doc_id=doc_id, image_url=metadata["image_url"], similarity=1 - distance)
            )
        return hits
