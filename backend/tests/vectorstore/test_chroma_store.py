import math
import zlib

from app.vectorstore.chroma_store import ChromaStore


class _FakeEmbeddingModel:
    """Deterministic bag-of-words hashing embedding, fast and offline for tests.

    Uses zlib.crc32 instead of the builtin hash() because str hashing is
    randomized per-process (PYTHONHASHSEED), which would make the "most
    similar document" assertions below flaky across test runs.
    """

    dims = 32

    def encode(self, texts: list[str]) -> list[list[float]]:
        return [self.encode_one(t) for t in texts]

    def encode_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dims
        for word in text.lower().split():
            vector[zlib.crc32(word.encode()) % self.dims] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


def _store(tmp_path) -> ChromaStore:
    return ChromaStore(persist_dir=str(tmp_path / "chroma"), embedding_model=_FakeEmbeddingModel())


def test_query_on_empty_collection_returns_no_hits(tmp_path):
    store = _store(tmp_path)
    assert store.query("anything", top_k=5) == []


def test_upsert_then_query_returns_most_similar_document_first(tmp_path):
    store = _store(tmp_path)
    store.upsert_documents(
        ids=["a", "b", "c"],
        texts=[
            "python is great for machine learning",
            "rust focuses on memory safety",
            "cooking pasta with tomato sauce",
        ],
    )
    hits = store.query("machine learning with python", top_k=3)
    assert hits[0].doc_id == "a"
    assert all(0.0 <= h.similarity <= 1.0 + 1e-6 for h in hits)


def test_upsert_is_idempotent_for_same_id(tmp_path):
    store = _store(tmp_path)
    store.upsert_documents(ids=["a"], texts=["first version"])
    store.upsert_documents(ids=["a"], texts=["second version, updated"])
    hits = store.query("updated", top_k=5)
    assert len(hits) == 1
