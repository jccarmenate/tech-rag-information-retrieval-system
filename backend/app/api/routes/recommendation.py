from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.models import Document
from app.db.session import get_db
from app.expansion.feedback_store import liked_doc_ids
from app.recommendation.recommender import recommend
from app.vectorstore.chroma_store import ChromaStore

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

_store = ChromaStore()


class RecommendationItem(BaseModel):
    doc_id: str
    title: str
    url: str
    source: str
    score: float


class RecommendationResponse(BaseModel):
    user_id: str
    results: list[RecommendationItem]


@router.get("", response_model=RecommendationResponse)
def get_recommendations(
    db: Annotated[Session, Depends(get_db)], user_id: str = "anonymous", top_k: int = 10
) -> RecommendationResponse:
    liked = liked_doc_ids(db, user_id)
    recommendations = recommend(db, _store, liked, top_k=top_k)

    docs = {
        d.id: d
        for d in db.query(Document).filter(Document.id.in_([r.doc_id for r in recommendations]))
    }
    results = [
        RecommendationItem(
            doc_id=r.doc_id,
            title=docs[r.doc_id].title,
            url=docs[r.doc_id].url,
            source=docs[r.doc_id].source,
            score=r.score,
        )
        for r in recommendations
        if r.doc_id in docs
    ]
    return RecommendationResponse(user_id=user_id, results=results)
