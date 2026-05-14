from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.rag.llm_providers.factory import get_llm_provider
from app.rag.pipeline import RagPipeline
from app.retrieval.service import get_retriever, get_vector_retriever

router = APIRouter(prefix="/api/rag", tags=["rag"])


class CitationOut(BaseModel):
    index: int
    doc_id: str
    title: str
    url: str
    source: str


class SourceOut(BaseModel):
    doc_id: str
    title: str
    url: str
    source: str


class RagAnswerResponse(BaseModel):
    query: str
    answer: str
    citations: list[CitationOut]
    sources: list[SourceOut]


@router.get("/answer", response_model=RagAnswerResponse)
def answer(q: str, db: Annotated[Session, Depends(get_db)], top_k: int = 5) -> RagAnswerResponse:
    pipeline = RagPipeline(
        db=db,
        retriever=get_retriever(),
        vector_retriever=get_vector_retriever(),
        llm_provider=get_llm_provider(),
        top_k=top_k,
    )
    result = pipeline.answer(q)
    return RagAnswerResponse(
        query=result.query,
        answer=result.answer,
        citations=[CitationOut(**c.__dict__) for c in result.citations],
        sources=[
            SourceOut(doc_id=s.doc_id, title=s.title, url=s.url, source=s.source)
            for s in result.sources
        ],
    )
