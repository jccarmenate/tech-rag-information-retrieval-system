from app.acquisition.connectors.base import BaseConnector
from app.acquisition.schemas import RawDocument
from app.acquisition.service import ingest_all
from app.db.models import Document


class _FakeConnector(BaseConnector):
    source_name = "fake"

    def __init__(self, docs: list[RawDocument]) -> None:
        super().__init__()
        self._docs = docs

    def fetch(self, limit: int = 20) -> list[RawDocument]:
        return self._docs[:limit]


class _FailingConnector(BaseConnector):
    source_name = "broken"

    def fetch(self, limit: int = 20) -> list[RawDocument]:
        raise RuntimeError("upstream is down")


def test_ingest_all_inserts_new_documents(db_session):
    doc = RawDocument.build(source="fake", url="https://x/1", title="T", text="body")
    result = ingest_all(db_session, connectors=[_FakeConnector([doc])])

    assert result.fetched == 1
    assert result.new == 1
    assert result.updated == 0
    assert db_session.query(Document).count() == 1


def test_ingest_all_updates_existing_documents(db_session):
    doc_v1 = RawDocument.build(source="fake", url="https://x/1", title="Old", text="old")
    doc_v2 = RawDocument.build(source="fake", url="https://x/1", title="New", text="new")

    ingest_all(db_session, connectors=[_FakeConnector([doc_v1])])
    result = ingest_all(db_session, connectors=[_FakeConnector([doc_v2])])

    assert result.new == 0
    assert result.updated == 1
    stored = db_session.get(Document, doc_v2.id)
    assert stored.title == "New"


def test_ingest_all_isolates_connector_failures(db_session):
    good_doc = RawDocument.build(source="fake", url="https://x/2", title="T", text="body")
    result = ingest_all(db_session, connectors=[_FailingConnector(), _FakeConnector([good_doc])])

    assert "broken" in result.errors
    assert result.new == 1
