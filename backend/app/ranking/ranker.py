import datetime
from dataclasses import dataclass

from app.ranking.signals import authority_signal, recency_signal

DEFAULT_WEIGHTS = {"relevance": 0.5, "recency": 0.2, "authority": 0.15, "feedback": 0.15}


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
    vector) considered relevant. The feedback signal is what lets the
    módulo de retroalimentación actually influence future rankings: a
    document users have upvoted for similar queries gets a boost, one
    they've downvoted gets pushed down.
    """

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self.weights = weights or DEFAULT_WEIGHTS

    def rank(
        self, candidates: list[RankCandidate], now: datetime.datetime | None = None
    ) -> list[RankedResult]:
        now = now or datetime.datetime.now(datetime.UTC)
        results = []
        for c in candidates:
            recency = recency_signal(c.published_at, now=now)
            authority = authority_signal(c.source)
            score = (
                self.weights["relevance"] * c.relevance
                + self.weights["recency"] * recency
                + self.weights["authority"] * authority
                + self.weights["feedback"] * c.feedback
            )
            results.append(
                RankedResult(
                    doc_id=c.doc_id,
                    score=score,
                    relevance=c.relevance,
                    recency=recency,
                    authority=authority,
                    feedback=c.feedback,
                )
            )
        results.sort(key=lambda r: r.score, reverse=True)
        return results
