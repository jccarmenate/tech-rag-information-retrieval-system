from app.recommendation import recommender as recommender_module
from app.recommendation.recommender import recommend
from app.retrieval.base import RetrievalResult


def test_recommend_returns_empty_for_user_with_no_likes(monkeypatch):
    assert recommend(db=None, store=None, liked_doc_ids=[], top_k=5) == []


def test_recommend_blends_content_and_collaborative_scores(monkeypatch):
    monkeypatch.setattr(
        recommender_module,
        "recommend_content_based",
        lambda store, liked_doc_ids, top_k: [RetrievalResult(doc_id="x", score=1.0)],
    )
    monkeypatch.setattr(
        recommender_module, "co_occurrence_scores", lambda db, liked_doc_ids: {"y": 1.0}
    )

    results = recommend(db=None, store=None, liked_doc_ids=["a"], top_k=5, content_weight=0.7)

    scores = {r.doc_id: r.score for r in results}
    assert scores["x"] == 0.7  # content_weight * 1.0 + (1 - content_weight) * 0.0
    assert round(scores["y"], 2) == 0.3  # content_weight * 0.0 + (1 - content_weight) * 1.0


def test_recommend_respects_top_k(monkeypatch):
    monkeypatch.setattr(
        recommender_module,
        "recommend_content_based",
        lambda store, liked_doc_ids, top_k: [
            RetrievalResult(doc_id="x", score=0.9),
            RetrievalResult(doc_id="y", score=0.5),
        ],
    )
    monkeypatch.setattr(recommender_module, "co_occurrence_scores", lambda db, liked_doc_ids: {})

    results = recommend(db=None, store=None, liked_doc_ids=["a"], top_k=1)

    assert len(results) == 1
    assert results[0].doc_id == "x"
