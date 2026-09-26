from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.ranking.ltr import prior_model
from app.ranking.service import get_ranking_model

router = APIRouter(prefix="/api/ranking", tags=["ranking"])


class RankingModelResponse(BaseModel):
    trained: bool  # false = too few (or single-class) votes, prior weights in use
    n_examples: int
    weights: dict[str, float]
    bias: float
    prior_weights: dict[str, float]
    metrics: dict[str, float]  # in-sample log-loss of the learned model vs the prior


@router.get("/model", response_model=RankingModelResponse)
def ranking_model(db: Annotated[Session, Depends(get_db)]) -> RankingModelResponse:
    model = get_ranking_model(db)
    return RankingModelResponse(
        trained=model.trained,
        n_examples=model.n_examples,
        weights=model.weights,
        bias=model.bias,
        prior_weights=prior_model().weights,
        metrics=model.metrics,
    )
