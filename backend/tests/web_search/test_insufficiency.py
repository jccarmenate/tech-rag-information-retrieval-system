from app.retrieval.base import RetrievalResult
from app.web_search.insufficiency import check_sufficiency


def test_no_hits_is_insufficient():
    report = check_sufficiency([])
    assert report.insufficient
    assert len(report.reasons) == 3  # fails quantity, quality, and coverage


def test_few_low_score_hits_is_insufficient():
    hits = [RetrievalResult(doc_id="a", score=0.1)]
    report = check_sufficiency(hits)
    assert report.insufficient


def test_enough_strong_hits_is_sufficient():
    hits = [
        RetrievalResult(doc_id="a", score=0.9),
        RetrievalResult(doc_id="b", score=0.8),
        RetrievalResult(doc_id="c", score=0.7),
    ]
    report = check_sufficiency(hits)
    assert not report.insufficient
    assert report.reasons == []


def test_one_strong_hit_among_weak_ones_is_still_insufficient_on_coverage():
    hits = [
        RetrievalResult(doc_id="a", score=0.95),
        RetrievalResult(doc_id="b", score=0.02),
        RetrievalResult(doc_id="c", score=0.02),
    ]
    report = check_sufficiency(hits, min_results=3, min_top_score=0.3, min_avg_score=0.4)
    assert report.insufficient
    assert report.reasons == ["average score 0.33 below threshold 0.4"]
