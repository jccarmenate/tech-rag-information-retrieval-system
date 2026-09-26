import threading

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import Feedback
from app.ranking.ltr import RankingModel, build_training_set, train
from app.ranking.ranker import Ranker

_lock = threading.Lock()
_cached: tuple[tuple[int, int], RankingModel] | None = None


def _feedback_fingerprint(db: Session) -> tuple[int, int]:
    count, max_id = db.query(func.count(Feedback.id), func.max(Feedback.id)).one()
    return count or 0, max_id or 0


def get_ranking_model(db: Session) -> RankingModel:
    """Returns the LTR model trained on the current feedback, retraining only
    when votes were added since the last training run.
    """
    global _cached
    fingerprint = _feedback_fingerprint(db)
    with _lock:
        if _cached is None or _cached[0] != fingerprint:
            _cached = (fingerprint, train(build_training_set(db)))
        return _cached[1]


def get_ranker(db: Session) -> Ranker:
    return Ranker(get_ranking_model(db))


def reset_ranking_cache() -> None:
    global _cached
    with _lock:
        _cached = None
