from dataclasses import dataclass

from app.recommendation.content_based import build_user_profile, recommend_content_based


@dataclass
class _FakeVectorHit:
    doc_id: str
    similarity: float


class _FakeStore:
    def __init__(self, embeddings: dict[str, list[float]], neighbors: list[_FakeVectorHit]):
        self._embeddings = embeddings
        self._neighbors = neighbors

    def get_document_embedding(self, doc_id: str) -> list[float] | None:
        return self._embeddings.get(doc_id)

    def query_by_vector(self, vector: list[float], top_k: int = 10) -> list[_FakeVectorHit]:
        return self._neighbors[:top_k]


def test_build_user_profile_averages_liked_embeddings():
    store = _FakeStore({"a": [1.0, 0.0], "b": [0.0, 1.0]}, [])
    profile = build_user_profile(store, ["a", "b"])
    assert profile == [0.5, 0.5]


def test_build_user_profile_is_none_for_cold_start_user():
    store = _FakeStore({}, [])
    assert build_user_profile(store, []) is None
    assert build_user_profile(store, ["unknown"]) is None


def test_recommend_content_based_excludes_already_liked_documents():
    store = _FakeStore(
        {"a": [1.0, 0.0]},
        [_FakeVectorHit(doc_id="a", similarity=0.99), _FakeVectorHit(doc_id="b", similarity=0.8)],
    )
    recommendations = recommend_content_based(store, liked_doc_ids=["a"], top_k=5)
    assert [r.doc_id for r in recommendations] == ["b"]


def test_recommend_content_based_returns_empty_for_cold_start():
    store = _FakeStore({}, [])
    assert recommend_content_based(store, liked_doc_ids=[], top_k=5) == []
