from sqlalchemy.orm import Session

from app.db.models import Document
from app.indexing.inverted_index import InvertedIndex
from app.indexing.store import save_index


def build_from_db(db: Session) -> InvertedIndex:
    index = InvertedIndex()
    documents = db.query(Document).all()
    index.build((doc.id, f"{doc.title}\n{doc.text}", doc.title) for doc in documents)
    return index


def build_and_save(db: Session) -> InvertedIndex:
    index = build_from_db(db)
    save_index(index)
    return index
