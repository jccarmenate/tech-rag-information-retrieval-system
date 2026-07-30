import math

from app.evaluation.metrics import (
    average_precision,
    mean_average_precision,
    mean_reciprocal_rank,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


def test_precision_at_k_counts_relevant_in_top_k():
    retrieved = ["a", "b", "c", "d"]
    relevant = {"a", "c"}
    assert precision_at_k(retrieved, relevant, k=4) == 0.5
    assert precision_at_k(retrieved, relevant, k=2) == 0.5
    assert precision_at_k(retrieved, relevant, k=1) == 1.0


def test_precision_at_k_empty_retrieved_is_zero():
    assert precision_at_k([], {"a"}, k=5) == 0.0


def test_recall_at_k_divides_by_total_relevant():
    retrieved = ["a", "x", "c"]
    relevant = {"a", "b", "c"}
    assert recall_at_k(retrieved, relevant, k=3) == 2 / 3


def test_recall_at_k_no_relevant_docs_is_zero():
    assert recall_at_k(["a"], set(), k=5) == 0.0


def test_average_precision_matches_hand_computed_value():
    # relevant docs at ranks 1 and 3: AP = (1/1 + 2/3) / 2
    retrieved = ["a", "x", "b", "y"]
    relevant = {"a", "b"}
    assert math.isclose(average_precision(retrieved, relevant), (1 / 1 + 2 / 3) / 2)


def test_average_precision_no_hits_is_zero():
    assert average_precision(["x", "y"], {"a"}) == 0.0


def test_mean_average_precision_averages_across_queries():
    all_retrieved = [["a", "x"], ["y", "b"]]
    all_relevant = [{"a"}, {"b"}]
    # AP query 1 = 1.0 (hit at rank 1), AP query 2 = 0.5 (hit at rank 2)
    assert mean_average_precision(all_retrieved, all_relevant) == 0.75


def test_reciprocal_rank_of_first_hit():
    assert reciprocal_rank(["x", "a", "y"], {"a"}) == 0.5
    assert reciprocal_rank(["a"], {"a"}) == 1.0
    assert reciprocal_rank(["x"], {"a"}) == 0.0


def test_mean_reciprocal_rank_averages_across_queries():
    all_retrieved = [["a"], ["x", "b"]]
    all_relevant = [{"a"}, {"b"}]
    assert mean_reciprocal_rank(all_retrieved, all_relevant) == (1.0 + 0.5) / 2


def test_ndcg_at_k_is_one_for_perfect_ranking():
    retrieved = ["a", "b", "c"]
    relevant = {"a", "b"}
    assert ndcg_at_k(retrieved, relevant, k=3) == 1.0


def test_ndcg_at_k_penalizes_relevant_docs_ranked_lower():
    perfect = ndcg_at_k(["a", "b", "x"], {"a", "b"}, k=3)
    worse = ndcg_at_k(["x", "a", "b"], {"a", "b"}, k=3)
    assert perfect > worse


def test_ndcg_at_k_with_no_relevant_docs_is_zero():
    assert ndcg_at_k(["a", "b"], set(), k=2) == 0.0
