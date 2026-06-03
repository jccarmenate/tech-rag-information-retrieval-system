from dataclasses import dataclass

from ddgs import DDGS


@dataclass
class WebResult:
    title: str
    url: str
    snippet: str


def search_web(query: str, max_results: int = 5) -> list[WebResult]:
    """Searches the public web via DuckDuckGo (no API key required).

    This is the module de búsqueda web: it only runs when the insufficiency
    checker decides the local corpus doesn't cover a query, so most searches
    never hit this function at all.
    """
    with DDGS() as ddgs:
        hits = ddgs.text(query, max_results=max_results)
    return [
        WebResult(title=hit.get("title", ""), url=hit.get("href", ""), snippet=hit.get("body", ""))
        for hit in hits
        if hit.get("href")
    ]
