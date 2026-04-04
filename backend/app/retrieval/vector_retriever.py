from app.retrieval.base import RetrievalResult, Retriever
from app.vectorstore.chroma_store import ChromaStore


class VectorRetriever(Retriever):
    """Semantic retrieval backed by sentence embeddings stored in ChromaDB.

    This is the second retrieval path (alongside the Bayesian Inference
    Network) that the RAG and ranking modules draw evidence from.
    """

    def __init__(self, store: ChromaStore | None = None) -> None:
        self.store = store or ChromaStore()

    def search(self, query: str, top_k: int = 10) -> list[RetrievalResult]:
        hits = self.store.query(query, top_k=top_k)
        return [RetrievalResult(doc_id=h.doc_id, score=h.similarity) for h in hits]
