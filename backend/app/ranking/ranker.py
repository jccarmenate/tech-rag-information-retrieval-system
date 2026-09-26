import datetime
from dataclasses import dataclass

from app.ranking.ltr import RankingModel, prior_model
from app.ranking.signals import authority_signal, recency_signal


@dataclass
class RankCandidate:
    doc_id: str
    relevance: float  # retriever score, already normalized to [0, 1]
    source: str
    published_at: datetime.datetime | None
    feedback: float = 0.5  # Laplace-smoothed positive-vote ratio, 0.5 = no feedback yet


@dataclass
class RankedResult:
    doc_id: str
    score: float
    relevance: float
    recency: float
    authority: float
    feedback: float


class Ranker:
    """Fuses retrieval relevance with recency, source authority and user feedback.

    This is the "posicionamiento" module: it decides the final order results
    are shown in, on top of whatever a retriever (inference network or
    vector) considered relevant. How much each signal counts is not hand-set:
    the weights come from a logistic model trained on users' 👍/👎 votes
    (see `ranking/ltr.py`), starting from — and regularised toward — a
    hand-set prior until enough votes exist.
    """

    def __init__(self, model: RankingModel | None = None) -> None:
        self.model = model or prior_model()

    def rank(
        self, candidates: list[RankCandidate], now: datetime.datetime | None = None
    ) -> list[RankedResult]:
        now = now or datetime.datetime.now(datetime.UTC)
        results = []
        for c in candidates:
            recency = recency_signal(c.published_at, now=now)
            authority = authority_signal(c.source)
            features = {
                "relevance": c.relevance,
                "recency": recency,
                "authority": authority,
                "feedback": c.feedback,
            }
            results.append(
                RankedResult(
                    doc_id=c.doc_id,
                    score=self.model.score(features),
                    relevance=c.relevance,
                    recency=recency,
                    authority=authority,
                    feedback=c.feedback,
                )
            )
        results.sort(key=lambda r: r.score, reverse=True)
        return results
