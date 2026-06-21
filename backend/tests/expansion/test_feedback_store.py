import pytest
from app.db.models import Base, Document
from app.expansion.feedback_store import feedback_score, record_feedback
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
    session.add(Document(id="doc-1", source="github", url="u", title="t", text="text"))
    session.commit()
    yield session
    session.close()


def test_feedback_score_is_neutral_with_no_votes(db_session):
    assert feedback_score(db_session, "doc-1") == 0.5


def test_feedback_score_increases_with_positive_votes(db_session):
    record_feedback(db_session, "query", "doc-1", 1)
    record_feedback(db_session, "query", "doc-1", 1)
    assert feedback_score(db_session, "doc-1") > 0.5


def test_feedback_score_decreases_with_negative_votes(db_session):
    record_feedback(db_session, "query", "doc-1", -1)
    record_feedback(db_session, "query", "doc-1", -1)
    assert feedback_score(db_session, "doc-1") < 0.5


def test_record_feedback_rejects_invalid_vote(db_session):
    with pytest.raises(ValueError):
        record_feedback(db_session, "query", "doc-1", 0)
