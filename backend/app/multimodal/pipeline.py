from sqlalchemy.orm import Session

from app.db.models import Document
from app.multimodal.image_store import ImageStore


def sync_images_from_db(db: Session, store: ImageStore | None = None) -> int:
    """Embeds and stores every document's image (if it has one). Returns how
    many were successfully embedded — image downloads can fail (dead link,
    timeout) without breaking the rest of the sync.
    """
    store = store or ImageStore()
    documents = db.query(Document).filter(Document.image_url.isnot(None)).all()
    synced = 0
    for doc in documents:
        if store.upsert_image(doc.id, doc.image_url):
            synced += 1
    return synced
