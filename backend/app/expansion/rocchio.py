from collections import defaultdict

from app.indexing.inverted_index import InvertedIndex
from app.indexing.tfidf import idf, tfidf_vector
from app.indexing.tokenizer import tokenize
from app.retrieval.base import Retriever

DEFAULT_ALPHA = 1.0  # weight kept on the original query terms
DEFAULT_BETA = 0.75  # weight given to the pseudo-relevant document centroid
DEFAULT_EXPANSION_TERMS = 5
DEFAULT_FEEDBACK_DOCS = 5


def expand_query_terms(
    query: str,
    index: InvertedIndex,
    feedback_doc_ids: list[str],
    *,
    alpha: float = DEFAULT_ALPHA,
    beta: float = DEFAULT_BETA,
    num_expansion_terms: int = DEFAULT_EXPANSION_TERMS,
) -> list[str]:
    """Rocchio pseudo-relevance feedback: assumes the top-ranked documents from
    a first-pass search are relevant and pulls the query vector toward their
    centroid, then returns the original terms plus the highest-weighted new
    terms from that centroid.

    No "non-relevant" set is used (this is the common simplification for
    query expansion, as opposed to full relevance feedback), so Rocchio's
    gamma/negative term is omitted.
    """
    query_terms = tokenize(query)
    combined: dict[str, float] = defaultdict(float)
    for term, count in _term_counts(query_terms).items():
        combined[term] += alpha * count * idf(term, index)

    doc_vectors = [tfidf_vector(doc_id, index) for doc_id in feedback_doc_ids]
    if doc_vectors:
        centroid_weight = beta / len(doc_vectors)
        for vector in doc_vectors:
            for term, weight in vector.items():
                combined[term] += centroid_weight * weight

    query_term_set = set(query_terms)
    new_terms = sorted(
        ((term, weight) for term, weight in combined.items() if term not in query_term_set),
        key=lambda item: item[1],
        reverse=True,
    )
    expansion_terms = [term for term, _ in new_terms[:num_expansion_terms]]
    return [*query_terms, *expansion_terms]


def _term_counts(terms: list[str]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for term in terms:
        counts[term] += 1
    return counts


def expand_query(
    query: str,
    retriever: Retriever,
    index: InvertedIndex,
    *,
    feedback_docs: int = DEFAULT_FEEDBACK_DOCS,
) -> str:
    """Runs a first-pass search to get pseudo-relevant documents, then
    returns an expanded query string built from their Rocchio centroid.
    """
    first_pass = retriever.search(query, top_k=feedback_docs)
    feedback_doc_ids = [hit.doc_id for hit in first_pass]
    expanded_terms = expand_query_terms(query, index, feedback_doc_ids)
    return " ".join(expanded_terms)
