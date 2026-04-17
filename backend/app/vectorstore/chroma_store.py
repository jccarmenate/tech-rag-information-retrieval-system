from dataclasses import dataclass

import chromadb

from app.core.config import get_settings
from app.vectorstore.chunker import chunk_text
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
        """Chunks each document and stores one embedded vector per chunk.

        Every chunk keeps a `doc_id` metadata pointer back to its parent so
        `query` can aggregate chunk hits into document-level results.
        """
        if not ids:
            return

        chunk_ids, chunk_texts, metadatas = [], [], []
        for doc_id, text in zip(ids, texts, strict=True):
            for i, chunk in enumerate(chunk_text(text)):
                chunk_ids.append(f"{doc_id}::{i}")
                chunk_texts.append(chunk)
                metadatas.append({"doc_id": doc_id})
        if not chunk_ids:
            return

        embeddings = self._embedder.encode(chunk_texts)
        for doc_id in ids:
            # drop any stale chunks from a previous, differently-sized version of this doc
            self._collection.delete(where={"doc_id": doc_id})
        self._collection.upsert(
            ids=chunk_ids, embeddings=embeddings, documents=chunk_texts, metadatas=metadatas
        )

    def query(self, text: str, top_k: int = 10) -> list[VectorHit]:
        count = self._collection.count()
        if count == 0:
            return []

        embedding = self._embedder.encode_one(text)
        n_results = min(count, max(top_k * 5, top_k))
        result = self._collection.query(query_embeddings=[embedding], n_results=n_results)

        best_per_doc: dict[str, float] = {}
        for metadata, distance in zip(result["metadatas"][0], result["distances"][0], strict=True):
            doc_id = metadata["doc_id"]
            similarity = 1 - distance  # cosine distance = 1 - cosine similarity
            if doc_id not in best_per_doc or similarity > best_per_doc[doc_id]:
                best_per_doc[doc_id] = similarity

        ranked = sorted(best_per_doc.items(), key=lambda kv: kv[1], reverse=True)
        return [VectorHit(doc_id=doc_id, similarity=sim) for doc_id, sim in ranked[:top_k]]
