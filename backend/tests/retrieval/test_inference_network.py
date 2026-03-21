from app.indexing.inverted_index import InvertedIndex
from app.retrieval.inference_network import InferenceNetworkRetriever


def _sample_index() -> InvertedIndex:
    index = InvertedIndex()
    index.build(
        [
            ("d1", "Python is great for machine learning and data science", "d1"),
            ("d2", "Rust is a systems programming language focused on safety", "d2"),
            ("d3", "Python and Rust interoperate through native bindings", "d3"),
        ]
    )
    return index


def test_search_ranks_matching_documents_above_non_matching():
    retriever = InferenceNetworkRetriever(_sample_index())
    results = retriever.search("python machine learning", top_k=5)
    doc_ids = [r.doc_id for r in results]
    assert "d1" in doc_ids
    assert "d2" not in doc_ids  # no query terms occur in d2


def test_search_scores_are_probabilities():
    retriever = InferenceNetworkRetriever(_sample_index())
    for result in retriever.search("python rust", top_k=5):
        assert 0.0 <= result.score <= 1.0


def test_link_weight_is_zero_when_term_absent():
    retriever = InferenceNetworkRetriever(_sample_index())
    assert retriever.link_weight("nonexistent", "d1") == 0.0


def test_link_weight_is_positive_when_term_present():
    retriever = InferenceNetworkRetriever(_sample_index())
    assert retriever.link_weight("python", "d1") > 0.0


def test_search_with_no_recognized_terms_returns_empty():
    retriever = InferenceNetworkRetriever(_sample_index())
    assert retriever.search("the a of", top_k=5) == []


def test_search_respects_top_k():
    retriever = InferenceNetworkRetriever(_sample_index())
    results = retriever.search("python rust", top_k=1)
    assert len(results) == 1
