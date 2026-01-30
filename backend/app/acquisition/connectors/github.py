from datetime import datetime

from app.acquisition.connectors.base import BaseConnector
from app.acquisition.schemas import RawDocument

SEARCH_URL = "https://api.github.com/search/repositories"


class GitHubConnector(BaseConnector):
    """Fetches actively updated, popular repositories from the GitHub Search API."""

    source_name = "github"

    def __init__(self, query: str = "stars:>500", token: str | None = None) -> None:
        super().__init__()
        self.query = query
        if token:
            self._client.headers["Authorization"] = f"Bearer {token}"
        self._client.headers["Accept"] = "application/vnd.github+json"

    def fetch(self, limit: int = 20) -> list[RawDocument]:
        data = self._get_json(
            SEARCH_URL,
            params={
                "q": self.query,
                "sort": "updated",
                "order": "desc",
                "per_page": min(limit, 100),
            },
        )
        items = data.get("items", []) if isinstance(data, dict) else []
        return [self._to_document(item) for item in items]

    def _to_document(self, item: dict) -> RawDocument:
        description = item.get("description") or ""
        topics = item.get("topics") or []
        language = item.get("language")
        tags = [*topics, language] if language else topics
        return RawDocument.build(
            source=self.source_name,
            url=item["html_url"],
            title=item["full_name"],
            text=description,
            image_url=item.get("owner", {}).get("avatar_url"),
            published_at=_parse_datetime(item.get("pushed_at")),
            tags=[t for t in tags if t],
        )


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
