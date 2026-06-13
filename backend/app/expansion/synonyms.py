import logging
from functools import lru_cache

import nltk

logger = logging.getLogger(__name__)

_WORDNET_READY = False


def _ensure_wordnet() -> bool:
    """Downloads the WordNet corpus on first use; returns False (never raises)
    if that isn't possible, e.g. no network access in a sandboxed CI run.
    """
    global _WORDNET_READY
    if _WORDNET_READY:
        return True
    try:
        nltk.data.find("corpora/wordnet")
    except LookupError:
        try:
            nltk.download("wordnet", quiet=True)
        except Exception as exc:  # pragma: no cover - environment dependent
            logger.warning("could not download WordNet corpus: %s", exc)
            return False
    _WORDNET_READY = True
    return True


@lru_cache(maxsize=512)
def get_synonyms(term: str, max_synonyms: int = 3) -> tuple[str, ...]:
    """Returns up to `max_synonyms` WordNet synonyms for a single word."""
    if not _ensure_wordnet():
        return ()

    from nltk.corpus import wordnet

    seen: dict[str, None] = {}
    for synset in wordnet.synsets(term):
        for lemma in synset.lemmas():
            name = lemma.name().replace("_", " ").lower()
            if name != term.lower():
                seen.setdefault(name, None)
    return tuple(seen)[:max_synonyms]


def expand_with_synonyms(terms: list[str], max_synonyms_per_term: int = 1) -> list[str]:
    expanded = list(terms)
    for term in terms:
        expanded.extend(get_synonyms(term, max_synonyms_per_term))
    return expanded
