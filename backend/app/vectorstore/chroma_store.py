from dataclasses import dataclass

import chromadb

from app.core.config import get_settings
from app.vectorstore.embeddings import EmbeddingModel

COLLECTION_NAME = "documents"


@dataclass
class VectorHit:
    doc_id: str
    similarity: float  # cosine similarity in [0, 1], higher is more relevant


class ChromaStore:
    def __init__(
        self, persist_dir: str | None = None, embedding_model: EmbeddingModel | None = None
    ) -> None:
        settings = get_settings()
        self._client = chromadb.PersistentClient(path=persist_dir or settings.chroma_persist_dir)
        self._collection = self._client.get_or_create_collection(
            COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )
        self._embedder = embedding_model or EmbeddingModel(settings.embedding_model_name)

    def upsert_documents(self, ids: list[str], texts: list[str]) -> None:
        if not ids:
            return
        embeddings = self._embedder.encode(texts)
        self._collection.upsert(ids=ids, embeddings=embeddings, documents=texts)

    def query(self, text: str, top_k: int = 10) -> list[VectorHit]:
        if self._collection.count() == 0:
            return []
        embedding = self._embedder.encode_one(text)
        result = self._collection.query(query_embeddings=[embedding], n_results=top_k)
        ids = result["ids"][0]
        distances = result["distances"][0]  # cosine distance = 1 - cosine similarity
        return [VectorHit(doc_id=i, similarity=1 - d) for i, d in zip(ids, distances, strict=True)]
