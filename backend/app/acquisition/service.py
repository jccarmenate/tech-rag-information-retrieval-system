import logging

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.acquisition.connectors.arxiv import ArxivConnector
from app.acquisition.connectors.base import BaseConnector
from app.acquisition.connectors.devto import DevToConnector
from app.acquisition.connectors.github import GitHubConnector
from app.acquisition.connectors.hackernews import HackerNewsConnector
from app.acquisition.connectors.stackexchange import StackExchangeConnector
from app.acquisition.schemas import RawDocument
from app.db.models import Document

logger = logging.getLogger(__name__)


def get_connectors(github_token: str | None = None) -> list[BaseConnector]:
    return [
        GitHubConnector(token=github_token),
        HackerNewsConnector(),
        DevToConnector(),
        StackExchangeConnector(),
        ArxivConnector(),
    ]


class IngestionResult(BaseModel):
    fetched: int = 0
    new: int = 0
    updated: int = 0
    errors: dict[str, str] = {}


def _upsert(db: Session, doc: RawDocument) -> bool:
    """Persists a RawDocument, returns True if it created a new row."""
    existing = db.get(Document, doc.id)
    if existing is None:
        db.add(
            Document(
                id=doc.id,
                source=doc.source,
                url=doc.url,
                title=doc.title,
                text=doc.text,
                image_url=doc.image_url,
                published_at=doc.published_at,
            )
        )
        return True

    existing.title = doc.title
    existing.text = doc.text
    existing.image_url = doc.image_url
    existing.published_at = doc.published_at
    return False


def ingest_all(
    db: Session, connectors: list[BaseConnector] | None = None, limit_per_source: int = 20
) -> IngestionResult:
    result = IngestionResult()
    for connector in connectors or get_connectors():
        with connector:
            try:
                docs = connector.fetch(limit=limit_per_source)
            except Exception as exc:  # a single failing source must not break the run
                logger.warning("connector %s failed: %s", connector.source_name, exc)
                result.errors[connector.source_name] = str(exc)
                continue

            result.fetched += len(docs)
            for doc in docs:
                if _upsert(db, doc):
                    result.new += 1
                else:
                    result.updated += 1

    db.commit()
    return result
