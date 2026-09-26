import datetime
import random

import pytest
from app.db.models import Base, Document, Feedback
from app.db.session import add_missing_columns
from app.expansion.feedback_store import record_feedback
from app.ranking.ltr import (
    FEATURES,
    MIN_EXAMPLES,
    PRIOR_WEIGHTS,
    Example,
    build_training_set,
    log_loss,
    prior_model,
    train,
)
from app.ranking.ranker import RankCandidate, Ranker
from app.ranking.service import get_ranking_model, reset_ranking_cache
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


def _engine():
    return create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )


@pytest.fixture
def db_session():
    engine = _engine()
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    session.add_all(
        [
            Document(id="a", source="arxiv", url="ua", title="A", text="t"),
            Document(id="b", source="devto", url="ub", title="B", text="t"),
        ]
    )
    session.commit()
    reset_ranking_cache()
    yield session
    session.close()
    reset_ranking_cache()


def _random_features(rng: random.Random) -> dict[str, float]:
    return {f: rng.random() for f in FEATURES}


def _recency_lover_votes(n: int, seed: int = 0) -> list[Example]:
    """Synthetic users who upvote recent results regardless of relevance."""
    rng = random.Random(seed)
    examples = []
    for _ in range(n):
        features = _random_features(rng)
        label = 1 if features["recency"] > 0.5 else 0
        examples.append(Example(features=features, label=label))
    return examples


def test_prior_preserves_the_fixed_weight_ordering():
    rng = random.Random(42)
    vectors = [_random_features(rng) for _ in range(50)]
    model = prior_model()

    by_prior = sorted(range(50), key=lambda i: model.score(vectors[i]))
    by_weighted_sum = sorted(
        range(50), key=lambda i: sum(PRIOR_WEIGHTS[f] * vectors[i][f] for f in FEATURES)
    )
    assert by_prior == by_weighted_sum


def test_too_few_votes_falls_back_to_the_prior():
    model = train(_recency_lover_votes(MIN_EXAMPLES - 1))
    assert not model.trained
    assert model.weights == prior_model().weights


def test_single_class_votes_fall_back_to_the_prior():
    examples = [Example(features={f: 0.5 for f in FEATURES}, label=1) for _ in range(50)]
    assert not train(examples).trained


def test_learns_a_preference_the_prior_does_not_have():
    model = train(_recency_lover_votes(300))

    assert model.trained
    assert model.weights["recency"] > prior_model().weights["recency"]

    now = datetime.datetime.now(datetime.UTC)
    old = now - datetime.timedelta(days=120)
    candidates = [
        RankCandidate(doc_id="relevant_old", relevance=0.9, source="devto", published_at=old),
        RankCandidate(doc_id="recent", relevance=0.3, source="devto", published_at=now),
    ]
    assert Ranker().rank(candidates, now=now)[0].doc_id == "relevant_old"
    assert Ranker(model).rank(candidates, now=now)[0].doc_id == "recent"


def test_learned_model_fits_the_votes_better_than_the_prior():
    examples = _recency_lover_votes(200)
    model = train(examples)
    assert log_loss(model, examples) < log_loss(prior_model(), examples)
    assert model.metrics["train_log_loss"] < model.metrics["prior_log_loss"]


def test_prior_dominates_small_samples_more_than_large_ones():
    prior_recency = prior_model().weights["recency"]
    small = train(_recency_lover_votes(25))
    large = train(_recency_lover_votes(400))
    assert small.weights["recency"] - prior_recency < large.weights["recency"] - prior_recency


def test_record_feedback_snapshots_ranking_features(db_session):
    with_features = record_feedback(db_session, "q", "a", 1, relevance=0.8)
    without = record_feedback(db_session, "q", "a", 1)

    assert with_features.relevance == 0.8
    assert with_features.authority == 0.9  # arxiv
    assert with_features.recency == 0.5  # unknown publish date
    assert without.relevance is None


def test_record_feedback_clamps_relevance(db_session):
    assert record_feedback(db_session, "q", "a", 1, relevance=1.7).relevance == 1.0


def test_training_set_skips_votes_without_features(db_session):
    record_feedback(db_session, "q", "a", 1, relevance=0.8)
    record_feedback(db_session, "q", "b", -1)
    examples = build_training_set(db_session)
    assert len(examples) == 1


def test_feedback_feature_excludes_the_vote_being_predicted(db_session):
    record_feedback(db_session, "q", "a", 1, relevance=0.8)
    [example] = build_training_set(db_session)
    # the document's only vote is this one, so leave-one-out sees no votes
    assert example.features["feedback"] == 0.5


def test_service_retrains_when_new_votes_arrive(db_session):
    assert not get_ranking_model(db_session).trained

    rng = random.Random(1)
    for i in range(60):
        doc_id = "a" if i % 2 else "b"
        record_feedback(db_session, f"q{i}", doc_id, 1 if i % 3 else -1, relevance=rng.random())

    model = get_ranking_model(db_session)
    assert model.trained
    assert model.n_examples == 60


def test_add_missing_columns_upgrades_an_old_feedback_table():
    engine = _engine()
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE feedback (id INTEGER PRIMARY KEY, query VARCHAR(512), "
                "doc_id VARCHAR(64), vote INTEGER, user_id VARCHAR(128), created_at DATETIME)"
            )
        )
    add_missing_columns(engine)

    columns = {c["name"] for c in inspect(engine).get_columns(Feedback.__tablename__)}
    assert {"relevance", "recency", "authority"} <= columns
