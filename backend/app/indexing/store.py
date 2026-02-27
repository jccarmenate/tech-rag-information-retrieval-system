import pickle
from pathlib import Path

from app.indexing.inverted_index import InvertedIndex

DEFAULT_INDEX_PATH = Path("data/index/inverted_index.pkl")


def save_index(index: InvertedIndex, path: Path = DEFAULT_INDEX_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        pickle.dump(index, f)


def load_index(path: Path = DEFAULT_INDEX_PATH) -> InvertedIndex | None:
    if not path.exists():
        return None
    with path.open("rb") as f:
        return pickle.load(f)
