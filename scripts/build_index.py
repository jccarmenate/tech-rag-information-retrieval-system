"""Rebuilds the inverted index from the documents currently stored in the database."""

from app.db.session import SessionLocal
from app.indexing.build_index import build_and_save

if __name__ == "__main__":
    db = SessionLocal()
    try:
        index = build_and_save(db)
        print(f"Indexed {index.n_docs} documents, vocabulary size {len(index.vocabulary)}")
    finally:
        db.close()
