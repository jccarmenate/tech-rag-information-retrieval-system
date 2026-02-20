from datetime import UTC, datetime

from app.acquisition.connectors.base import BaseConnector
from app.acquisition.schemas import RawDocument

SEARCH_URL = "https://hn.algolia.com/api/v1/search"


class HackerNewsConnector(BaseConnector):
    """Fetches current front-page stories using the Algolia HN Search API."""

    source_name = "hackernews"

    def fetch(self, limit: int = 20) -> list[RawDocument]:
        data = self._get_json(SEARCH_URL, params={"tags": "front_page", "hitsPerPage": limit})
        hits = data.get("hits", []) if isinstance(data, dict) else []
        return [self._to_document(hit) for hit in hits if hit.get("title")]

    def _to_document(self, hit: dict) -> RawDocument:
        hn_url = f"https://news.ycombinator.com/item?id={hit['objectID']}"
        return RawDocument.build(
            source=self.source_name,
            url=hit.get("url") or hn_url,
            title=hit["title"],
            text=hit.get("story_text") or hit.get("title", ""),
            published_at=_parse_timestamp(hit.get("created_at_i")),
            tags=["hackernews"],
        )


def _parse_timestamp(value: int | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromtimestamp(value, tz=UTC)
