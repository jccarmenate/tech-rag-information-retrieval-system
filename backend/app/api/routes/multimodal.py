from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.models import Document
from app.db.session import get_db
from app.multimodal.image_store import ImageStore

router = APIRouter(prefix="/api/multimodal", tags=["multimodal"])

_store = ImageStore()


class ImageResultItem(BaseModel):
    doc_id: str
    title: str
    url: str
    image_url: str
    similarity: float


class ImageSearchResponse(BaseModel):
    query: str
    results: list[ImageResultItem]


@router.get("/search", response_model=ImageSearchResponse)
def search_images(
    q: str, db: Annotated[Session, Depends(get_db)], top_k: int = 10
) -> ImageSearchResponse:
    """Text-to-image search: a plain text query is embedded with CLIP and
    matched against document images embedded the same way.
    """
    hits = _store.query_by_text(q, top_k=top_k)
    docs = {d.id: d for d in db.query(Document).filter(Document.id.in_([h.doc_id for h in hits]))}
    results = [
        ImageResultItem(
            doc_id=hit.doc_id,
            title=docs[hit.doc_id].title,
            url=docs[hit.doc_id].url,
            image_url=hit.image_url,
            similarity=hit.similarity,
        )
        for hit in hits
        if hit.doc_id in docs
    ]
    return ImageSearchResponse(query=q, results=results)
