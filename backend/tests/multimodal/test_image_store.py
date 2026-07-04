import math
import zlib

from app.multimodal.image_store import ImageStore


class _FakeClipModel:
    """Deterministic fake embedding: same hashing trick used to fake sentence
    embeddings in the vectorstore tests, treating the "image" as its URL
    string so tests stay fast and offline.
    """

    dims = 16

    def encode_text(self, text: str) -> list[float]:
        return self._encode(text)

    def fetch_and_encode_image(self, url: str, timeout: float = 15.0) -> list[float] | None:
        if url == "unreachable://broken":
            return None
        return self._encode(url)

    def _encode(self, text: str) -> list[float]:
        vector = [0.0] * self.dims
        for word in text.lower().replace("/", " ").replace(".", " ").split():
            vector[zlib.crc32(word.encode()) % self.dims] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


def _store(tmp_path) -> ImageStore:
    return ImageStore(persist_dir=str(tmp_path / "chroma"), embedding_model=_FakeClipModel())


def test_upsert_image_returns_false_when_download_fails(tmp_path):
    store = _store(tmp_path)
    assert store.upsert_image("doc-1", "unreachable://broken") is False


def test_query_on_empty_collection_returns_no_hits(tmp_path):
    store = _store(tmp_path)
    assert store.query_by_text("python logo", top_k=5) == []


def test_upsert_then_query_returns_matching_image(tmp_path):
    store = _store(tmp_path)
    store.upsert_image("doc-python", "https://example.com/python-logo.png")
    store.upsert_image("doc-rust", "https://example.com/rust-crab.png")

    hits = store.query_by_text("https://example.com/python-logo.png", top_k=2)

    assert hits[0].doc_id == "doc-python"
    assert hits[0].image_url == "https://example.com/python-logo.png"
