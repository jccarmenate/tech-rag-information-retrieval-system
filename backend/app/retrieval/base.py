from abc import ABC, abstractmethod

from pydantic import BaseModel


class RetrievalResult(BaseModel):
    doc_id: str
    score: float


class Retriever(ABC):
    """Common interface every retrieval model (classic or non-basic) implements."""

    @abstractmethod
    def search(self, query: str, top_k: int = 10) -> list[RetrievalResult]:
        raise NotImplementedError
