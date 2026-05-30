from dataclasses import dataclass

from app.retrieval.base import RetrievalResult


@dataclass
class InsufficiencyReport:
    insufficient: bool
    reasons: list[str]


def check_sufficiency(
    hits: list[RetrievalResult],
    *,
    min_results: int = 3,
    min_top_score: float = 0.35,
    min_avg_score: float = 0.2,
) -> InsufficiencyReport:
    """Decides whether the local corpus has enough to answer, or the web search
    fallback module should kick in.

    Three independent criteria, any of which can trigger the fallback:
    - quantity: too few candidate documents matched at all
    - quality: even the best match is weak
    - coverage: the average relevance across matches is weak (a single lucky
      hit surrounded by noise shouldn't count as "enough")
    """
    reasons = []

    if len(hits) < min_results:
        reasons.append(f"only {len(hits)} local result(s), need at least {min_results}")

    top_score = hits[0].score if hits else 0.0
    if top_score < min_top_score:
        reasons.append(f"top score {top_score:.2f} below threshold {min_top_score}")

    avg_score = sum(h.score for h in hits) / len(hits) if hits else 0.0
    if avg_score < min_avg_score:
        reasons.append(f"average score {avg_score:.2f} below threshold {min_avg_score}")

    return InsufficiencyReport(insufficient=bool(reasons), reasons=reasons)
