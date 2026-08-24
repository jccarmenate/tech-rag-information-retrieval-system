from app.retrieval.base import RetrievalResult
from app.web_search import pipeline as pipeline_module
from app.web_search.pipeline import augment_if_needed


def test_augment_skips_web_search_when_local_results_are_sufficient(monkeypatch):
    called = False

    def _fail_if_called(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("search_web should not be called when local results suffice")

    monkeypatch.setattr(pipeline_module, "search_web", _fail_if_called)

    hits = [RetrievalResult(doc_id=f"d{i}", score=0.9) for i in range(3)]
    merged, used_fallback = augment_if_needed("query", hits, db=None)

    assert not called
    assert used_fallback is False
    assert merged == hits


def test_augment_degrades_gracefully_when_web_search_raises(monkeypatch):
    def _raise(*args, **kwargs):
        raise RuntimeError("network unreachable")

    monkeypatch.setattr(pipeline_module, "search_web", _raise)

    merged, used_fallback = augment_if_needed("query", [], db=None)

    assert used_fallback is False
    assert merged == []


def test_augment_returns_local_results_when_web_search_finds_nothing(monkeypatch):
    monkeypatch.setattr(pipeline_module, "search_web", lambda query, max_results: [])

    hits = [RetrievalResult(doc_id="a", score=0.1)]
    merged, used_fallback = augment_if_needed("query", hits, db=None)

    assert used_fallback is False
    assert merged == hits


def test_augment_merges_web_hits_when_search_succeeds(monkeypatch):
    from app.web_search.searcher import WebResult

    monkeypatch.setattr(
        pipeline_module,
        "search_web",
        lambda query, max_results: [WebResult(title="T", url="https://x", snippet="s")],
    )
    monkeypatch.setattr(pipeline_module, "index_web_results", lambda db, results: ["new-doc"])

    merged, used_fallback = augment_if_needed("query", [], db=None)

    assert used_fallback is True
    assert [h.doc_id for h in merged] == ["new-doc"]
