from app.indexing.inverted_index import InvertedIndex
from app.indexing.tfidf import cosine_similarity, idf, tfidf_vector


def _sample_index() -> InvertedIndex:
    index = InvertedIndex()
    index.build(
        [
            ("d1", "Python machine learning tutorial", "d1"),
            ("d2", "Rust systems programming tutorial", "d2"),
            ("d3", "Python data science tutorial", "d3"),
        ]
    )
    return index


def test_idf_is_lower_for_common_terms():
    index = _sample_index()
    assert idf("tutorial", index) < idf("rust", index)


def test_tfidf_vector_only_contains_present_terms():
    index = _sample_index()
    vector = tfidf_vector("d2", index)
    assert "rust" in vector
    assert "python" not in vector


def test_cosine_similarity_ranks_more_similar_document_higher():
    index = _sample_index()
    query_vector = tfidf_vector("d3", index)  # reuse d3 as a stand-in for a python-ish query
    sim_d1 = cosine_similarity(query_vector, tfidf_vector("d1", index))
    sim_d2 = cosine_similarity(query_vector, tfidf_vector("d2", index))
    assert sim_d1 > sim_d2


def test_cosine_similarity_handles_disjoint_vocabularies():
    assert cosine_similarity({"a": 1.0}, {"b": 1.0}) == 0.0
