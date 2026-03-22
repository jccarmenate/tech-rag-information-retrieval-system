from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.models import Document
from app.db.session import get_db
from app.retrieval.service import get_retriever

router = APIRouter(prefix="/api/search", tags=["search"])


class SearchResultItem(BaseModel):
    doc_id: str
    title: str
    url: str
    source: str
    score: float
    snippet: str


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]


def _snippet(text: str, length: int = 240) -> str:
    text = text.strip()
    return text if len(text) <= length else text[:length].rsplit(" ", 1)[0] + "..."


@router.get("", response_model=SearchResponse)
def search(q: str, db: Annotated[Session, Depends(get_db)], top_k: int = 10) -> SearchResponse:
    retriever = get_retriever()
    hits = retriever.search(q, top_k=top_k)
    if not hits:
        return SearchResponse(query=q, results=[])

    docs = {d.id: d for d in db.query(Document).filter(Document.id.in_([h.doc_id for h in hits]))}
    results = [
        SearchResultItem(
            doc_id=hit.doc_id,
            title=docs[hit.doc_id].title,
            url=docs[hit.doc_id].url,
            source=docs[hit.doc_id].source,
            score=hit.score,
            snippet=_snippet(docs[hit.doc_id].text),
        )
        for hit in hits
        if hit.doc_id in docs
    ]
    return SearchResponse(query=q, results=results)
