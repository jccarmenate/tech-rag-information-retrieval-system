import pytest
from app.db.models import Base, Document
from app.rag.pipeline import RagPipeline
from app.retrieval.base import RetrievalResult
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


class _FakeRetriever:
    def __init__(self, hits: list[RetrievalResult]) -> None:
        self._hits = hits

    def search(self, query: str, top_k: int = 10) -> list[RetrievalResult]:
        return self._hits[:top_k]


class _FakeLLM:
    def __init__(self, response: str) -> None:
        self.response = response
        self.last_prompt: str | None = None

    def generate(self, prompt: str, system: str | None = None) -> str:
        self.last_prompt = prompt
        return self.response


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    session.add_all(
        [
            Document(id="a", source="github", url="urlA", title="Repo A", text="Python ML library"),
            Document(
                id="b", source="devto", url="urlB", title="Article B", text="Rust systems post"
            ),
        ]
    )
    session.commit()
    yield session
    session.close()


def test_answer_merges_hits_from_both_retrievers_without_duplicates(db_session):
    inference = _FakeRetriever([RetrievalResult(doc_id="a", score=0.9)])
    vector = _FakeRetriever(
        [RetrievalResult(doc_id="a", score=0.8), RetrievalResult(doc_id="b", score=0.7)]
    )
    llm = _FakeLLM("Uses Python [1] and Rust [2].")

    pipeline = RagPipeline(db_session, inference, vector, llm, top_k=5)
    result = pipeline.answer("python and rust")

    assert [s.doc_id for s in result.sources] == ["a", "b"]
    assert [c.doc_id for c in result.citations] == ["a", "b"]
    assert "[1]" in llm.last_prompt


def test_answer_with_no_hits_skips_llm_call(db_session):
    llm = _FakeLLM("should not be used")
    pipeline = RagPipeline(db_session, _FakeRetriever([]), _FakeRetriever([]), llm, top_k=5)

    result = pipeline.answer("nothing relevant")

    assert result.sources == []
    assert result.citations == []
    assert llm.last_prompt is None


def test_answer_respects_top_k_across_merged_retrievers(db_session):
    inference = _FakeRetriever([RetrievalResult(doc_id="a", score=0.9)])
    vector = _FakeRetriever([RetrievalResult(doc_id="b", score=0.7)])
    llm = _FakeLLM("Combined answer.")

    pipeline = RagPipeline(db_session, inference, vector, llm, top_k=1)
    result = pipeline.answer("query")

    assert len(result.sources) == 1
