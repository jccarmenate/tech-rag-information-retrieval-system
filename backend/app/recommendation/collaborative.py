from collections import defaultdict

from sqlalchemy.orm import Session

from app.db.models import Feedback


def co_occurrence_scores(db: Session, seed_doc_ids: list[str]) -> dict[str, float]:
    """A lightweight item-item collaborative signal: documents that were
    upvoted for the same query as one of the seed documents get a score
    proportional to how often that co-occurred, normalized to [0, 1].

    This stands in for full user-user collaborative filtering, which needs
    far more users/history than a freshly-deployed system has — co-visitation
    within queries is usable from day one.
    """
    if not seed_doc_ids:
        return {}

    seed_set = set(seed_doc_ids)
    rows = db.query(Feedback.query, Feedback.doc_id).filter(Feedback.vote == 1).all()

    docs_by_query: dict[str, set[str]] = defaultdict(set)
    for query, doc_id in rows:
        docs_by_query[query].add(doc_id)

    co_counts: dict[str, int] = defaultdict(int)
    for doc_ids_in_query in docs_by_query.values():
        if not doc_ids_in_query & seed_set:
            continue
        for doc_id in doc_ids_in_query - seed_set:
            co_counts[doc_id] += 1

    if not co_counts:
        return {}

    max_count = max(co_counts.values())
    return {doc_id: count / max_count for doc_id, count in co_counts.items()}
