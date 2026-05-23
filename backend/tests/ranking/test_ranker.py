import datetime

from app.ranking.ranker import RankCandidate, Ranker


def test_rank_orders_by_combined_score_descending():
    now = datetime.datetime.now(datetime.UTC)
    candidates = [
        RankCandidate(doc_id="low", relevance=0.2, source="hackernews", published_at=now),
        RankCandidate(doc_id="high", relevance=0.9, source="arxiv", published_at=now),
    ]
    ranked = Ranker().rank(candidates, now=now)
    assert [r.doc_id for r in ranked] == ["high", "low"]


def test_relevance_weight_dominates_by_default():
    now = datetime.datetime.now(datetime.UTC)
    old = now - datetime.timedelta(days=365)
    candidates = [
        RankCandidate(doc_id="relevant_old", relevance=0.95, source="devto", published_at=old),
        RankCandidate(doc_id="irrelevant_new", relevance=0.1, source="devto", published_at=now),
    ]
    ranked = Ranker().rank(candidates, now=now)
    assert ranked[0].doc_id == "relevant_old"


def test_custom_weights_change_ordering():
    now = datetime.datetime.now(datetime.UTC)
    old = now - datetime.timedelta(days=365)
    candidates = [
        RankCandidate(doc_id="relevant_old", relevance=0.95, source="devto", published_at=old),
        RankCandidate(doc_id="irrelevant_new", relevance=0.1, source="devto", published_at=now),
    ]
    recency_focused = Ranker(weights={"relevance": 0.1, "recency": 0.8, "authority": 0.1})
    ranked = recency_focused.rank(candidates, now=now)
    assert ranked[0].doc_id == "irrelevant_new"


def test_rank_returns_component_scores():
    now = datetime.datetime.now(datetime.UTC)
    candidates = [RankCandidate(doc_id="a", relevance=0.5, source="github", published_at=now)]
    result = Ranker().rank(candidates, now=now)[0]
    assert result.relevance == 0.5
    assert 0.0 <= result.recency <= 1.0
    assert 0.0 <= result.authority <= 1.0
