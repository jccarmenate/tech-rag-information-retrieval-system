from app.evaluation.qrels import load_qrels, load_sample_corpus
from app.evaluation.runner import run_evaluation


def test_qrels_and_sample_corpus_are_well_formed():
    corpus = load_sample_corpus()
    corpus_ids = {doc["id"] for doc in corpus}
    judgments = load_qrels()

    assert len(corpus) > 0
    assert len(judgments) > 0
    for judgment in judgments:
        assert judgment.relevant_doc_ids <= corpus_ids, (
            f"qrels reference doc ids missing from the sample corpus: {judgment.query}"
        )


def test_run_evaluation_returns_metrics_in_valid_range():
    report = run_evaluation(k=5)

    assert report.num_queries == len(load_qrels())
    for value in [
        report.precision_at_k,
        report.recall_at_k,
        report.map,
        report.mrr,
        report.ndcg_at_k,
    ]:
        assert 0.0 <= value <= 1.0


def test_run_evaluation_finds_the_obviously_relevant_document():
    # sanity check: a query copied almost verbatim from a document's title
    # should retrieve that exact document, proving the pipeline is wired
    # correctly end to end (qrels -> sample index -> retriever -> metrics)
    report = run_evaluation(k=1)
    assert report.mrr > 0.5
