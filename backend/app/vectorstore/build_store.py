from sqlalchemy.orm import Session

from app.db.models import Document
from app.vectorstore.chroma_store import ChromaStore


def sync_from_db(db: Session, store: ChromaStore | None = None) -> int:
    """Upserts every document's title+text into the vector store. Returns the count synced."""
    store = store or ChromaStore()
    documents = db.query(Document).all()
    ids = [doc.id for doc in documents]
    texts = [f"{doc.title}\n{doc.text}" for doc in documents]
    store.upsert_documents(ids, texts)
    return len(ids)
