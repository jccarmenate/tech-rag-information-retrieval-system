from collections import Counter, defaultdict
from collections.abc import Iterable

from app.indexing.tokenizer import tokenize


class InvertedIndex:
    """A term -> {doc_id: term_frequency} inverted index with document stats.

    This is the shared data structure the classic (TF-IDF weighted) index
    relies on, and it also feeds the term-document statistics used to build
    the Bayesian Inference Network retriever.
    """

    def __init__(self) -> None:
        self.postings: dict[str, dict[str, int]] = defaultdict(dict)
        self.doc_lengths: dict[str, int] = {}
        self.doc_titles: dict[str, str] = {}

    @property
    def vocabulary(self) -> list[str]:
        return list(self.postings.keys())

    @property
    def n_docs(self) -> int:
        return len(self.doc_lengths)

    def add_document(self, doc_id: str, text: str, title: str = "") -> None:
        tokens = tokenize(text)
        self.doc_lengths[doc_id] = len(tokens)
        self.doc_titles[doc_id] = title
        term_counts = Counter(tokens)
        for term, count in term_counts.items():
            self.postings[term][doc_id] = count

    def build(self, documents: Iterable[tuple[str, str, str]]) -> None:
        """documents: iterable of (doc_id, text, title)."""
        self.postings.clear()
        self.doc_lengths.clear()
        self.doc_titles.clear()
        for doc_id, text, title in documents:
            self.add_document(doc_id, text, title)

    def document_frequency(self, term: str) -> int:
        return len(self.postings.get(term, {}))

    def term_frequency(self, term: str, doc_id: str) -> int:
        return self.postings.get(term, {}).get(doc_id, 0)

    def documents_containing(self, term: str) -> set[str]:
        return set(self.postings.get(term, {}).keys())
