from app.expansion.rocchio import expand_query, expand_query_terms
from app.indexing.inverted_index import InvertedIndex
from app.retrieval.inference_network import InferenceNetworkRetriever


def _sample_index() -> InvertedIndex:
    index = InvertedIndex()
    index.build(
        [
            (
                "d1",
                "Python is great for machine learning and neural networks",
                "d1",
            ),
            (
                "d2",
                "Deep learning frameworks like PyTorch and TensorFlow use Python",
                "d2",
            ),
            ("d3", "Rust focuses on memory safety and systems programming", "d3"),
        ]
    )
    return index


def test_expand_query_terms_keeps_original_terms():
    index = _sample_index()
    expanded = expand_query_terms("python machine learning", index, feedback_doc_ids=["d1", "d2"])
    assert {"python", "machine", "learning"} <= set(expanded)


def test_expand_query_terms_adds_new_terms_from_feedback_docs():
    index = _sample_index()
    expanded = expand_query_terms("python machine learning", index, feedback_doc_ids=["d1", "d2"])
    assert len(expanded) > len({"python", "machine", "learning"})


def test_expand_query_terms_with_no_feedback_docs_returns_original_only():
    index = _sample_index()
    expanded = expand_query_terms("rust safety", index, feedback_doc_ids=[])
    assert expanded == ["rust", "safety"]


def test_expand_query_uses_first_pass_retrieval_for_feedback_docs():
    index = _sample_index()
    retriever = InferenceNetworkRetriever(index)
    expanded = expand_query("python machine learning", retriever, index, feedback_docs=2)
    assert "python" in expanded
    assert isinstance(expanded, str)
