from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.models import Document
from app.db.session import get_db
from app.ranking.ranker import RankCandidate, Ranker
from app.retrieval.base import RetrievalResult
from app.retrieval.service import get_retriever, get_vector_retriever

router = APIRouter(prefix="/api/search", tags=["search"])

RetrievalMode = Literal["inference_network", "vector"]

_ranker = Ranker()


class SearchResultItem(BaseModel):
    doc_id: str
    title: str
    url: str
    source: str
    score: float  # final position score (relevance + recency + authority)
    relevance: float  # raw retriever score, before ranking
    snippet: str


class SearchResponse(BaseModel):
    query: str
    mode: RetrievalMode
    results: list[SearchResultItem]


def _snippet(text: str, length: int = 240) -> str:
    text = text.strip()
    return text if len(text) <= length else text[:length].rsplit(" ", 1)[0] + "..."


def _rank_and_hydrate(
    hits: list[RetrievalResult], db: Session, top_k: int
) -> list[SearchResultItem]:
    if not hits:
        return []

    docs = {d.id: d for d in db.query(Document).filter(Document.id.in_([h.doc_id for h in hits]))}
    relevance_by_id = {h.doc_id: h.score for h in hits if h.doc_id in docs}
    candidates = [
        RankCandidate(
            doc_id=doc_id,
            relevance=relevance,
            source=docs[doc_id].source,
            published_at=docs[doc_id].published_at,
        )
        for doc_id, relevance in relevance_by_id.items()
    ]
    ranked = _ranker.rank(candidates)[:top_k]
    return [
        SearchResultItem(
            doc_id=r.doc_id,
            title=docs[r.doc_id].title,
            url=docs[r.doc_id].url,
            source=docs[r.doc_id].source,
            score=r.score,
            relevance=r.relevance,
            snippet=_snippet(docs[r.doc_id].text),
        )
        for r in ranked
    ]


@router.get("", response_model=SearchResponse)
def search(
    q: str,
    db: Annotated[Session, Depends(get_db)],
    top_k: int = 10,
    mode: RetrievalMode = "inference_network",
) -> SearchResponse:
    retriever = get_retriever() if mode == "inference_network" else get_vector_retriever()
    # over-fetch candidates so the ranker has real headroom to reorder by
    # recency/authority instead of just re-sorting an already-truncated top_k
    hits = retriever.search(q, top_k=top_k * 3)
    results = _rank_and_hydrate(hits, db, top_k)
    return SearchResponse(query=q, mode=mode, results=results)
