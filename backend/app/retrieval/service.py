from functools import lru_cache

from app.indexing.inverted_index import InvertedIndex
from app.indexing.store import load_index
from app.retrieval.inference_network import InferenceNetworkRetriever
from app.retrieval.vector_retriever import VectorRetriever


@lru_cache
def _cached_retriever() -> InferenceNetworkRetriever:
    index = load_index() or InvertedIndex()
    return InferenceNetworkRetriever(index)


def get_retriever() -> InferenceNetworkRetriever:
    return _cached_retriever()


@lru_cache
def get_vector_retriever() -> VectorRetriever:
    return VectorRetriever()


def reset_retriever_cache() -> None:
    """Call after the index is rebuilt so the next search picks up fresh data."""
    _cached_retriever.cache_clear()
