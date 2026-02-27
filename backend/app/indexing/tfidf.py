import math

from app.indexing.inverted_index import InvertedIndex


def idf(term: str, index: InvertedIndex) -> float:
    """Smoothed inverse document frequency: log((N + 1) / (df + 1)) + 1."""
    df = index.document_frequency(term)
    return math.log((index.n_docs + 1) / (df + 1)) + 1.0


def tf(term: str, doc_id: str, index: InvertedIndex) -> float:
    """Sublinear term frequency: 1 + log(raw_tf), 0 when the term is absent."""
    raw = index.term_frequency(term, doc_id)
    return 1.0 + math.log(raw) if raw > 0 else 0.0


def tfidf_vector(doc_id: str, index: InvertedIndex) -> dict[str, float]:
    return {
        term: tf(term, doc_id, index) * idf(term, index)
        for term in index.postings
        if index.term_frequency(term, doc_id) > 0
    }


def cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    shared_terms = vec_a.keys() & vec_b.keys()
    if not shared_terms:
        return 0.0
    dot = sum(vec_a[t] * vec_b[t] for t in shared_terms)
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
