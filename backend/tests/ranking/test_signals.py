import datetime

from app.ranking.signals import authority_signal, recency_signal


def test_authority_signal_uses_known_source_weight():
    assert authority_signal("arxiv") > authority_signal("hackernews")


def test_authority_signal_falls_back_to_default_for_unknown_source():
    assert authority_signal("some-new-blog") == 0.5


def test_recency_signal_is_one_for_now():
    now = datetime.datetime.now(datetime.UTC)
    assert recency_signal(now, now=now) == 1.0


def test_recency_signal_decays_with_age():
    now = datetime.datetime.now(datetime.UTC)
    recent = now - datetime.timedelta(days=1)
    old = now - datetime.timedelta(days=365)
    assert recency_signal(recent, now=now) > recency_signal(old, now=now)


def test_recency_signal_is_neutral_when_unknown():
    assert recency_signal(None) == 0.5


def test_recency_signal_handles_naive_datetimes():
    now = datetime.datetime.now(datetime.UTC)
    naive_recent = (now - datetime.timedelta(days=1)).replace(tzinfo=None)
    assert 0.0 < recency_signal(naive_recent, now=now) < 1.0
