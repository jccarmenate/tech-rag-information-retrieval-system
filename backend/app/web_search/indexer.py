from sqlalchemy.orm import Session

from app.acquisition.schemas import RawDocument
from app.acquisition.service import upsert_document
from app.web_search.searcher import WebResult


def index_web_results(db: Session, results: list[WebResult]) -> list[str]:
    """Persists DuckDuckGo hits as regular documents (source="web").

    This lets a web-search fallback answer double as free corpus growth: the
    next time a similar query comes in, the result may already be indexed
    locally and the fallback won't need to trigger at all.
    """
    doc_ids = []
    for result in results:
        if not result.title or not result.url:
            continue
        doc = RawDocument.build(
            source="web", url=result.url, title=result.title, text=result.snippet
        )
        upsert_document(db, doc)
        doc_ids.append(doc.id)

    db.commit()
    return doc_ids
