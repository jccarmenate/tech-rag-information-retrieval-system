import datetime
from dataclasses import dataclass

from app.ranking.signals import authority_signal, recency_signal

DEFAULT_WEIGHTS = {"relevance": 0.6, "recency": 0.25, "authority": 0.15}


@dataclass
class RankCandidate:
    doc_id: str
    relevance: float  # retriever score, already normalized to [0, 1]
    source: str
    published_at: datetime.datetime | None


@dataclass
class RankedResult:
    doc_id: str
    score: float
    relevance: float
    recency: float
    authority: float


class Ranker:
    """Fuses retrieval relevance with recency and source authority.

    This is the "posicionamiento" module: it decides the final order results
    are shown in, on top of whatever a retriever (inference network or
    vector) considered relevant. Weights are configurable so the feedback
    module (module de retroalimentación) can later learn/tune them from user
    signal instead of using this fixed default.
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
            )
            results.append(
                RankedResult(
                    doc_id=c.doc_id,
                    score=score,
                    relevance=c.relevance,
                    recency=recency,
                    authority=authority,
                )
            )
        results.sort(key=lambda r: r.score, reverse=True)
        return results
