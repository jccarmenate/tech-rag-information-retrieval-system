from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.expansion.feedback_store import record_feedback

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    query: str
    doc_id: str
    vote: Literal[1, -1]


class FeedbackResponse(BaseModel):
    id: int
    query: str
    doc_id: str
    vote: int


@router.post("", response_model=FeedbackResponse)
def submit_feedback(
    payload: FeedbackRequest, db: Annotated[Session, Depends(get_db)]
) -> FeedbackResponse:
    feedback = record_feedback(db, payload.query, payload.doc_id, payload.vote)
    return FeedbackResponse(
        id=feedback.id, query=feedback.query, doc_id=feedback.doc_id, vote=feedback.vote
    )
