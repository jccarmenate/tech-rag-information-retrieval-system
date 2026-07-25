import pytest
from app.db.models import Base, Document
from app.expansion.feedback_store import record_feedback
from app.recommendation.collaborative import co_occurrence_scores
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    for doc_id in ["a", "b", "c"]:
        session.add(Document(id=doc_id, source="github", url=doc_id, title=doc_id, text="t"))
    session.commit()
    yield session
    session.close()


def test_no_seed_docs_returns_empty(db_session):
    assert co_occurrence_scores(db_session, []) == {}


def test_finds_documents_co_liked_in_the_same_query(db_session):
    record_feedback(db_session, "python tips", "a", 1, user_id="alice")
    record_feedback(db_session, "python tips", "b", 1, user_id="bob")

    scores = co_occurrence_scores(db_session, seed_doc_ids=["a"])

    assert scores == {"b": 1.0}


def test_ignores_negative_votes(db_session):
    record_feedback(db_session, "python tips", "a", 1, user_id="alice")
    record_feedback(db_session, "python tips", "b", -1, user_id="bob")

    scores = co_occurrence_scores(db_session, seed_doc_ids=["a"])

    assert scores == {}


def test_excludes_seed_documents_from_results(db_session):
    record_feedback(db_session, "python tips", "a", 1, user_id="alice")
    record_feedback(db_session, "python tips", "c", 1, user_id="carol")

    scores = co_occurrence_scores(db_session, seed_doc_ids=["a", "c"])

    assert scores == {}
