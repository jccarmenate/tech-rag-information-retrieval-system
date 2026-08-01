from pydantic import BaseModel

from app.evaluation.metrics import (
    mean_average_precision,
    mean_reciprocal_rank,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)
from app.evaluation.qrels import load_qrels, load_sample_corpus
from app.indexing.inverted_index import InvertedIndex
from app.retrieval.inference_network import InferenceNetworkRetriever

DEFAULT_K = 5


class EvaluationReport(BaseModel):
    num_queries: int
    k: int
    precision_at_k: float
    recall_at_k: float
    map: float
    mrr: float
    ndcg_at_k: float


def _build_sample_index() -> InvertedIndex:
    """Builds a small, frozen index from the hand-curated sample corpus.

    Evaluating against this fixed corpus (rather than the live, constantly
    refreshed acquisition corpus) is what makes the reported metrics
    reproducible run to run.
    """
    index = InvertedIndex()
    documents = load_sample_corpus()
    index.build((doc["id"], f"{doc['title']}\n{doc['text']}", doc["title"]) for doc in documents)
    return index


def run_evaluation(k: int = DEFAULT_K) -> EvaluationReport:
    index = _build_sample_index()
    retriever = InferenceNetworkRetriever(index)
    judgments = load_qrels()

    all_retrieved: list[list[str]] = []
    all_relevant: list[set[str]] = []
    precisions, recalls, ndcgs = [], [], []

    for judgment in judgments:
        hits = retriever.search(judgment.query, top_k=k)
        retrieved_ids = [hit.doc_id for hit in hits]
        all_retrieved.append(retrieved_ids)
        all_relevant.append(judgment.relevant_doc_ids)
        precisions.append(precision_at_k(retrieved_ids, judgment.relevant_doc_ids, k))
        recalls.append(recall_at_k(retrieved_ids, judgment.relevant_doc_ids, k))
        ndcgs.append(ndcg_at_k(retrieved_ids, judgment.relevant_doc_ids, k))

    n = len(judgments)
    return EvaluationReport(
        num_queries=n,
        k=k,
        precision_at_k=sum(precisions) / n if n else 0.0,
        recall_at_k=sum(recalls) / n if n else 0.0,
        map=mean_average_precision(all_retrieved, all_relevant),
        mrr=mean_reciprocal_rank(all_retrieved, all_relevant),
        ndcg_at_k=sum(ndcgs) / n if n else 0.0,
    )
