from sqlalchemy.orm import Session

from app.retrieval.base import RetrievalResult
from app.web_search.indexer import index_web_results
from app.web_search.insufficiency import check_sufficiency
from app.web_search.searcher import search_web

# Web hits are indexed on the spot but not yet folded into the persisted
# inverted index / vector store (that happens on the next acquisition
# refresh), so they're given a fixed, moderate relevance score here rather
# than a comparable one from a retrieval model.
WEB_FALLBACK_SCORE = 0.5


def augment_if_needed(
    query: str, hits: list[RetrievalResult], db: Session, max_web_results: int = 5
) -> tuple[list[RetrievalResult], bool]:
    """Runs the web search fallback when local retrieval is insufficient.

    Returns the (possibly augmented) hit list and whether the fallback fired,
    so callers can surface that to the user ("results include live web
    search" vs. "answered entirely from the local corpus").
    """
    report = check_sufficiency(hits)
    if not report.insufficient:
        return hits, False

    web_results = search_web(query, max_results=max_web_results)
    if not web_results:
        return hits, False

    new_doc_ids = index_web_results(db, web_results)
    web_hits = [RetrievalResult(doc_id=doc_id, score=WEB_FALLBACK_SCORE) for doc_id in new_doc_ids]

    known_ids = {h.doc_id for h in hits}
    merged = hits + [h for h in web_hits if h.doc_id not in known_ids]
    return merged, True
