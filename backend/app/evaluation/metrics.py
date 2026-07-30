import math


def precision_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    top_k = retrieved[:k]
    if not top_k:
        return 0.0
    return sum(1 for doc_id in top_k if doc_id in relevant) / len(top_k)


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    top_k = retrieved[:k]
    return sum(1 for doc_id in top_k if doc_id in relevant) / len(relevant)


def average_precision(retrieved: list[str], relevant: set[str]) -> float:
    """AP for a single query — the building block for MAP across many queries."""
    if not relevant:
        return 0.0
    hits = 0
    precisions = []
    for i, doc_id in enumerate(retrieved, start=1):
        if doc_id in relevant:
            hits += 1
            precisions.append(hits / i)
    return sum(precisions) / len(relevant) if precisions else 0.0


def mean_average_precision(all_retrieved: list[list[str]], all_relevant: list[set[str]]) -> float:
    if not all_retrieved:
        return 0.0
    scores = [
        average_precision(retrieved, relevant)
        for retrieved, relevant in zip(all_retrieved, all_relevant, strict=True)
    ]
    return sum(scores) / len(scores)


def reciprocal_rank(retrieved: list[str], relevant: set[str]) -> float:
    for i, doc_id in enumerate(retrieved, start=1):
        if doc_id in relevant:
            return 1 / i
    return 0.0


def mean_reciprocal_rank(all_retrieved: list[list[str]], all_relevant: list[set[str]]) -> float:
    if not all_retrieved:
        return 0.0
    scores = [
        reciprocal_rank(retrieved, relevant)
        for retrieved, relevant in zip(all_retrieved, all_relevant, strict=True)
    ]
    return sum(scores) / len(scores)


def ndcg_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    """Binary-relevance nDCG@k (graded relevance isn't needed for our qrels)."""
    top_k = retrieved[:k]
    dcg = sum(1 / math.log2(i + 1) for i, doc_id in enumerate(top_k, start=1) if doc_id in relevant)
    ideal_hits = min(len(relevant), k)
    idcg = sum(1 / math.log2(i + 1) for i in range(1, ideal_hits + 1))
    return dcg / idcg if idcg > 0 else 0.0
