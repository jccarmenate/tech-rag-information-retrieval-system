from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.recommendation.collaborative import co_occurrence_scores
from app.recommendation.content_based import recommend_content_based
from app.vectorstore.chroma_store import ChromaStore

DEFAULT_CONTENT_WEIGHT = 0.7


@dataclass
class Recommendation:
    doc_id: str
    score: float


def recommend(
    db: Session,
    store: ChromaStore,
    liked_doc_ids: list[str],
    top_k: int = 10,
    content_weight: float = DEFAULT_CONTENT_WEIGHT,
) -> list[Recommendation]:
    """Hybrid recommender: blends a content-based signal (similarity to the
    user's liked-document centroid) with a collaborative one (documents
    co-liked with the user's likes across other queries/users).

    A user with no likes yet gets an empty list — there's nothing to base a
    recommendation on until they've given the system at least one signal.
    """
    if not liked_doc_ids:
        return []

    content_hits = {
        hit.doc_id: hit.score
        for hit in recommend_content_based(store, liked_doc_ids, top_k=top_k * 2)
    }
    collaborative_scores = co_occurrence_scores(db, liked_doc_ids)

    candidate_ids = set(content_hits) | set(collaborative_scores)
    collaborative_weight = 1 - content_weight
    scored = [
        Recommendation(
            doc_id=doc_id,
            score=content_weight * content_hits.get(doc_id, 0.0)
            + collaborative_weight * collaborative_scores.get(doc_id, 0.0),
        )
        for doc_id in candidate_ids
    ]
    scored.sort(key=lambda r: r.score, reverse=True)
    return scored[:top_k]
