import xml.etree.ElementTree as ET
from datetime import datetime

from app.acquisition.connectors.base import BaseConnector
from app.acquisition.schemas import RawDocument

QUERY_URL = "http://export.arxiv.org/api/query"
ATOM_NS = "{http://www.w3.org/2005/Atom}"


class ArxivConnector(BaseConnector):
    """Fetches recent papers from arXiv's Atom API for CS categories."""

    source_name = "arxiv"

    def __init__(self, categories: tuple[str, ...] = ("cs.SE", "cs.AI", "cs.CL")) -> None:
        super().__init__()
        self.search_query = " OR ".join(f"cat:{c}" for c in categories)

    def fetch(self, limit: int = 20) -> list[RawDocument]:
        response = self._client.get(
            QUERY_URL,
            params={
                "search_query": self.search_query,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
                "max_results": limit,
            },
        )
        response.raise_for_status()
        root = ET.fromstring(response.text)
        entries = root.findall(f"{ATOM_NS}entry")
        return [self._to_document(entry) for entry in entries]

    def _to_document(self, entry: ET.Element) -> RawDocument:
        title = (entry.findtext(f"{ATOM_NS}title") or "").strip().replace("\n", " ")
        summary = (entry.findtext(f"{ATOM_NS}summary") or "").strip()
        url = entry.findtext(f"{ATOM_NS}id") or ""
        published = entry.findtext(f"{ATOM_NS}published")
        tags = [c.attrib.get("term", "") for c in entry.findall(f"{ATOM_NS}category")]
        return RawDocument.build(
            source=self.source_name,
            url=url,
            title=title,
            text=summary,
            published_at=_parse_datetime(published),
            tags=[t for t in tags if t],
        )


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
