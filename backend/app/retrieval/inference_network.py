"""Bayesian Inference Network retrieval model (Turtle & Croft, 1991).

This is the "non-basic" retrieval model required by the project: instead of a
plain vector-space cosine ranking, relevance is modeled as a belief network:

    document nodes (d_i) -> concept/term nodes (r_k) -> query node (q)

Each document node is root evidence (P(d_i) is uniform, documents are
independent). A directed link d_i -> r_k carries P(r_k | d_i): how strongly
document i "brings about" concept k, estimated from a tf-idf-normalized
weight (the estimate proposed by Turtle & Croft, also used in INQUERY).

The query node combines the term nodes that appear in the query through the
canonical "noisy-OR" belief combination, i.e. it treats each matching concept
as an independent piece of evidence for relevance and asks: what is the
probability that at least one of them, weighted by how much the query cares
about it, actually supports the query?

    P(q | d_i) = 1 - prod_{k in query} (1 - P(r_k|d_i) * P(q|r_k))

Documents are ranked by P(q | d_i).
"""

from collections import defaultdict

from app.indexing.inverted_index import InvertedIndex
from app.indexing.tfidf import idf
from app.indexing.tokenizer import tokenize
from app.retrieval.base import RetrievalResult, Retriever


class InferenceNetworkRetriever(Retriever):
    def __init__(self, index: InvertedIndex) -> None:
        self.index = index
        self._doc_max_tf: dict[str, int] = defaultdict(int)
        for postings in index.postings.values():
            for doc_id, tf in postings.items():
                if tf > self._doc_max_tf[doc_id]:
                    self._doc_max_tf[doc_id] = tf
        self._max_idf = max((idf(t, index) for t in index.vocabulary), default=1.0)

    def link_weight(self, term: str, doc_id: str) -> float:
        """P(r_k | d_i), Turtle & Croft's tf-idf based link matrix estimate."""
        raw_tf = self.index.term_frequency(term, doc_id)
        if raw_tf == 0:
            return 0.0
        max_tf = self._doc_max_tf.get(doc_id, 1) or 1
        term_idf = idf(term, self.index)
        normalized_idf = term_idf / self._max_idf if self._max_idf else 0.0
        # 0.4 baseline + 0.6 scaled component keeps P(r_k|d_i) in (0.4, 1.0]
        # whenever the term occurs at all, and 0 otherwise (Turtle & Croft 1991).
        return 0.4 + 0.6 * (raw_tf / max_tf) * normalized_idf

    def query_term_weight(self, term: str, query_terms: list[str]) -> float:
        """P(q | r_k): how much the query node trusts concept r_k."""
        term_idf = idf(term, self.index)
        return term_idf / self._max_idf if self._max_idf else 0.0

    def score(self, query_terms: list[str], doc_id: str) -> float:
        belief_of_no_evidence = 1.0
        for term in query_terms:
            p_rk_di = self.link_weight(term, doc_id)
            if p_rk_di == 0.0:
                continue
            p_q_rk = self.query_term_weight(term, query_terms)
            belief_of_no_evidence *= 1 - p_rk_di * p_q_rk
        return 1 - belief_of_no_evidence

    def search(self, query: str, top_k: int = 10) -> list[RetrievalResult]:
        query_terms = list(dict.fromkeys(tokenize(query)))  # dedupe, keep order
        if not query_terms:
            return []

        candidate_docs: set[str] = set()
        for term in query_terms:
            candidate_docs |= self.index.documents_containing(term)

        scored = [
            RetrievalResult(doc_id=doc_id, score=self.score(query_terms, doc_id))
            for doc_id in candidate_docs
        ]
        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:top_k]
