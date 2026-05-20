import datetime

# How much each source is trusted as a starting point for the authority signal.
# Peer-reviewed papers and heavily-starred repositories are weighted above
# forum questions and blog posts, which in turn outrank raw discussion threads.
SOURCE_AUTHORITY = {
    "arxiv": 0.9,
    "github": 0.85,
    "stackexchange": 0.75,
    "devto": 0.6,
    "hackernews": 0.55,
}
DEFAULT_AUTHORITY = 0.5

RECENCY_HALF_LIFE_DAYS = 30


def authority_signal(source: str) -> float:
    return SOURCE_AUTHORITY.get(source, DEFAULT_AUTHORITY)


def recency_signal(
    published_at: datetime.datetime | None,
    now: datetime.datetime | None = None,
    half_life_days: float = RECENCY_HALF_LIFE_DAYS,
) -> float:
    """Exponential decay: 1.0 when published now, 0.5 after one half-life, etc.

    Documents with an unknown publish date get a neutral 0.5 rather than
    being penalized as if they were old.
    """
    if published_at is None:
        return 0.5

    now = now or datetime.datetime.now(datetime.UTC)
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=datetime.UTC)

    age_days = max((now - published_at).total_seconds() / 86400, 0)
    return 0.5 ** (age_days / half_life_days)
