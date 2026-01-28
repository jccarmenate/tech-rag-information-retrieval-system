import datetime
import hashlib

from pydantic import BaseModel, Field


def document_id(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:24]


class RawDocument(BaseModel):
    """Normalized document produced by every acquisition connector."""

    id: str
    source: str
    url: str
    title: str
    text: str
    image_url: str | None = None
    published_at: datetime.datetime | None = None
    tags: list[str] = Field(default_factory=list)

    @classmethod
    def build(
        cls,
        *,
        source: str,
        url: str,
        title: str,
        text: str,
        image_url: str | None = None,
        published_at: datetime.datetime | None = None,
        tags: list[str] | None = None,
    ) -> "RawDocument":
        return cls(
            id=document_id(url),
            source=source,
            url=url,
            title=title.strip(),
            text=text.strip(),
            image_url=image_url,
            published_at=published_at,
            tags=tags or [],
        )
