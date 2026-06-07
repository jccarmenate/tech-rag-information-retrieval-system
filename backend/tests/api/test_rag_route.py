from app.api.routes import rag as rag_route
from app.rag import pipeline as pipeline_module
from app.retrieval.base import RetrievalResult


class _FakeRetriever:
    def search(self, query: str, top_k: int = 10) -> list[RetrievalResult]:
        return [RetrievalResult(doc_id="doc-1", score=0.9)]


class _EmptyRetriever:
    def search(self, query: str, top_k: int = 10) -> list[RetrievalResult]:
        return []


class _FakeLLM:
    def generate(self, prompt: str, system: str | None = None) -> str:
        return "Python is great for ML [1]."


def test_rag_answer_returns_generated_text_and_citations(client_with_docs, monkeypatch):
    client, _ = client_with_docs
    monkeypatch.setattr(rag_route, "get_retriever", lambda: _FakeRetriever())
    monkeypatch.setattr(rag_route, "get_vector_retriever", lambda: _EmptyRetriever())
    monkeypatch.setattr(rag_route, "get_llm_provider", lambda: _FakeLLM())
    monkeypatch.setattr(pipeline_module, "augment_if_needed", lambda query, hits, db: (hits, False))

    response = client.get("/api/rag/answer", params={"q": "python for ml"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Python is great for ML [1]."
    assert body["citations"][0]["doc_id"] == "doc-1"
    assert body["sources"][0]["title"] == "A great Python repo"


def test_rag_answer_with_no_sources_returns_fallback_message(client_with_docs, monkeypatch):
    client, _ = client_with_docs
    monkeypatch.setattr(rag_route, "get_retriever", lambda: _EmptyRetriever())
    monkeypatch.setattr(rag_route, "get_vector_retriever", lambda: _EmptyRetriever())
    monkeypatch.setattr(rag_route, "get_llm_provider", lambda: _FakeLLM())
    monkeypatch.setattr(pipeline_module, "augment_if_needed", lambda query, hits, db: (hits, False))

    response = client.get("/api/rag/answer", params={"q": "nothing"})

    assert response.json()["sources"] == []
    assert response.json()["citations"] == []
