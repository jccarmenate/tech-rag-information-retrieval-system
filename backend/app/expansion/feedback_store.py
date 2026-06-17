from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import Feedback


def record_feedback(db: Session, query: str, doc_id: str, vote: int) -> Feedback:
    if vote not in (1, -1):
        raise ValueError("vote must be 1 (relevant) or -1 (not relevant)")
    feedback = Feedback(query=query, doc_id=doc_id, vote=vote)
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def feedback_score(db: Session, doc_id: str) -> float:
    """Laplace-smoothed positive-vote ratio in [0, 1], 0.5 when there's no
    feedback yet (neutral, doesn't help or hurt a document's ranking).
    """
    positive = (
        db.query(func.count(Feedback.id)).filter(Feedback.doc_id == doc_id, Feedback.vote == 1)
    ).scalar()
    negative = (
        db.query(func.count(Feedback.id)).filter(Feedback.doc_id == doc_id, Feedback.vote == -1)
    ).scalar()
    return (positive + 1) / (positive + negative + 2)
