from app.indexing.inverted_index import InvertedIndex


def _sample_index() -> InvertedIndex:
    index = InvertedIndex()
    index.build(
        [
            ("d1", "Python is a great language for machine learning", "Python for ML"),
            ("d2", "Rust is a systems language focused on safety", "Rust safety"),
            ("d3", "Python and Rust can be used together via bindings", "Python + Rust"),
        ]
    )
    return index


def test_document_frequency_counts_matching_documents():
    index = _sample_index()
    assert index.document_frequency("python") == 2
    assert index.document_frequency("rust") == 2
    assert index.document_frequency("bindings") == 1
    assert index.document_frequency("nonexistent") == 0


def test_term_frequency_counts_occurrences_per_document():
    index = _sample_index()
    assert index.term_frequency("python", "d1") == 1
    assert index.term_frequency("python", "d2") == 0


def test_documents_containing_returns_expected_set():
    index = _sample_index()
    assert index.documents_containing("rust") == {"d2", "d3"}


def test_n_docs_and_vocabulary():
    index = _sample_index()
    assert index.n_docs == 3
    assert "python" in index.vocabulary
    assert "the" not in index.vocabulary  # stopword
