from datetime import UTC, datetime

from app.acquisition.connectors.base import BaseConnector
from app.acquisition.schemas import RawDocument

QUESTIONS_URL = "https://api.stackexchange.com/2.3/questions"


class StackExchangeConnector(BaseConnector):
    """Fetches recently active Stack Overflow questions via the StackExchange API."""

    source_name = "stackexchange"

    def __init__(self, site: str = "stackoverflow") -> None:
        super().__init__()
        self.site = site

    def fetch(self, limit: int = 20) -> list[RawDocument]:
        data = self._get_json(
            QUESTIONS_URL,
            params={
                "order": "desc",
                "sort": "activity",
                "site": self.site,
                "pagesize": min(limit, 100),
            },
        )
        items = data.get("items", []) if isinstance(data, dict) else []
        return [self._to_document(item) for item in items]

    def _to_document(self, item: dict) -> RawDocument:
        tags = item.get("tags") or []
        return RawDocument.build(
            source=self.source_name,
            url=item["link"],
            title=item["title"],
            text=f"{item['title']} ({', '.join(tags)})",
            published_at=_parse_timestamp(item.get("creation_date")),
            tags=tags,
        )


def _parse_timestamp(value: int | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromtimestamp(value, tz=UTC)
