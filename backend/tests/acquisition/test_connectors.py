import respx
from app.acquisition.connectors.arxiv import ArxivConnector
from app.acquisition.connectors.devto import DevToConnector
from app.acquisition.connectors.github import GitHubConnector
from app.acquisition.connectors.hackernews import HackerNewsConnector
from app.acquisition.connectors.stackexchange import StackExchangeConnector
from httpx import Response

ARXIV_ENTRY = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2601.00001v1</id>
    <title>  A Study on Retrieval Augmented Generation  </title>
    <summary>We study RAG systems.</summary>
    <published>2026-01-05T00:00:00Z</published>
    <category term="cs.AI"/>
  </entry>
</feed>
"""


@respx.mock
def test_github_connector_parses_repositories():
    respx.get("https://api.github.com/search/repositories").mock(
        return_value=Response(
            200,
            json={
                "items": [
                    {
                        "html_url": "https://github.com/octo/repo",
                        "full_name": "octo/repo",
                        "description": "A repo",
                        "topics": ["python"],
                        "language": "Python",
                        "pushed_at": "2026-01-10T12:00:00Z",
                        "owner": {"avatar_url": "https://avatars/octo.png"},
                    }
                ]
            },
        )
    )
    with GitHubConnector() as connector:
        docs = connector.fetch(limit=10)
    assert len(docs) == 1
    assert docs[0].title == "octo/repo"
    assert "python" in docs[0].tags


@respx.mock
def test_hackernews_connector_falls_back_to_hn_url():
    respx.get("https://hn.algolia.com/api/v1/search").mock(
        return_value=Response(
            200,
            json={
                "hits": [
                    {
                        "objectID": "123",
                        "title": "Ask HN: something",
                        "url": None,
                        "created_at_i": 1_700_000_000,
                    }
                ]
            },
        )
    )
    with HackerNewsConnector() as connector:
        docs = connector.fetch(limit=10)
    assert docs[0].url == "https://news.ycombinator.com/item?id=123"


@respx.mock
def test_devto_connector_parses_articles():
    respx.get("https://dev.to/api/articles").mock(
        return_value=Response(
            200,
            json=[
                {
                    "url": "https://dev.to/a/1",
                    "title": "Article",
                    "description": "desc",
                    "cover_image": "https://img/1.png",
                    "published_at": "2026-01-05T00:00:00Z",
                    "tag_list": ["webdev"],
                }
            ],
        )
    )
    with DevToConnector() as connector:
        docs = connector.fetch(limit=10)
    assert docs[0].tags == ["webdev"]


@respx.mock
def test_stackexchange_connector_parses_questions():
    respx.get("https://api.stackexchange.com/2.3/questions").mock(
        return_value=Response(
            200,
            json={
                "items": [
                    {
                        "link": "https://stackoverflow.com/q/1",
                        "title": "How do I do X?",
                        "tags": ["python"],
                        "creation_date": 1_700_000_000,
                    }
                ]
            },
        )
    )
    with StackExchangeConnector() as connector:
        docs = connector.fetch(limit=10)
    assert docs[0].tags == ["python"]


@respx.mock
def test_arxiv_connector_parses_atom_feed():
    respx.get("https://export.arxiv.org/api/query").mock(
        return_value=Response(200, text=ARXIV_ENTRY, headers={"content-type": "application/atom+xml"})
    )
    with ArxivConnector() as connector:
        docs = connector.fetch(limit=10)
    assert docs[0].title == "A Study on Retrieval Augmented Generation"
    assert "cs.AI" in docs[0].tags
