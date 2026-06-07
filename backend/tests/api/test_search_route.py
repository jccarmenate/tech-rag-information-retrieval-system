from app.api.routes import search as search_route
from app.retrieval.base import RetrievalResult


class _FakeRetriever:
    def search(self, query: str, top_k: int = 10) -> list[RetrievalResult]:
        return [RetrievalResult(doc_id="doc-1", score=0.9)]


def _no_web_fallback(monkeypatch):
    monkeypatch.setattr(search_route, "augment_if_needed", lambda query, hits, db: (hits, False))


def test_search_returns_hydrated_results(client_with_docs, monkeypatch):
    client, _ = client_with_docs
    monkeypatch.setattr(search_route, "get_retriever", lambda: _FakeRetriever())
    _no_web_fallback(monkeypatch)

    response = client.get("/api/search", params={"q": "python machine learning"})

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "inference_network"
    assert body["used_web_fallback"] is False
    assert body["results"][0]["doc_id"] == "doc-1"
    assert body["results"][0]["title"] == "A great Python repo"


def test_search_vector_mode_uses_vector_retriever(client_with_docs, monkeypatch):
    client, _ = client_with_docs
    monkeypatch.setattr(search_route, "get_vector_retriever", lambda: _FakeRetriever())
    _no_web_fallback(monkeypatch)

    response = client.get("/api/search", params={"q": "python", "mode": "vector"})

    assert response.status_code == 200
    assert response.json()["mode"] == "vector"
    assert len(response.json()["results"]) == 1


def test_search_with_no_hits_returns_empty_results(client_with_docs, monkeypatch):
    client, _ = client_with_docs

    class _EmptyRetriever:
        def search(self, query: str, top_k: int = 10) -> list[RetrievalResult]:
            return []

    monkeypatch.setattr(search_route, "get_retriever", lambda: _EmptyRetriever())
    _no_web_fallback(monkeypatch)

    response = client.get("/api/search", params={"q": "nothing matches"})

    assert response.json()["results"] == []


def test_search_triggers_web_fallback_when_flagged(client_with_docs, monkeypatch):
    client, _ = client_with_docs
    monkeypatch.setattr(search_route, "get_retriever", lambda: _FakeRetriever())
    monkeypatch.setattr(search_route, "augment_if_needed", lambda query, hits, db: (hits, True))

    response = client.get("/api/search", params={"q": "python machine learning"})

    assert response.json()["used_web_fallback"] is True
