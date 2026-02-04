from datetime import datetime

from app.acquisition.connectors.base import BaseConnector
from app.acquisition.schemas import RawDocument

ARTICLES_URL = "https://dev.to/api/articles"


class DevToConnector(BaseConnector):
    """Fetches top recent articles from the Dev.to public API."""

    source_name = "devto"

    def fetch(self, limit: int = 20) -> list[RawDocument]:
        data = self._get_json(ARTICLES_URL, params={"top": 7, "per_page": limit})
        items = data if isinstance(data, list) else []
        return [self._to_document(item) for item in items]

    def _to_document(self, item: dict) -> RawDocument:
        return RawDocument.build(
            source=self.source_name,
            url=item["url"],
            title=item["title"],
            text=item.get("description") or "",
            image_url=item.get("cover_image") or item.get("social_image"),
            published_at=_parse_datetime(item.get("published_at")),
            tags=item.get("tag_list") or [],
        )


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
