from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.db.models import Document
from app.rag.llm_providers.base import LLMProvider
from app.rag.prompts import SYSTEM_PROMPT, ContextChunk, build_prompt
from app.retrieval.base import Retriever

CONTEXT_CHARS = 800


@dataclass
class RagAnswer:
    query: str
    answer: str
    sources: list[ContextChunk]


def _merge_hit_ids(*hit_lists: list, top_k: int) -> list[str]:
    """Unions doc ids from multiple retrievers, keeping first-seen order (dedup)."""
    seen: dict[str, None] = {}
    for hits in hit_lists:
        for hit in hits:
            seen.setdefault(hit.doc_id, None)
    return list(seen)[:top_k]


class RagPipeline:
    def __init__(
        self,
        db: Session,
        retriever: Retriever,
        vector_retriever: Retriever,
        llm_provider: LLMProvider,
        top_k: int = 5,
    ) -> None:
        self.db = db
        self.retriever = retriever
        self.vector_retriever = vector_retriever
        self.llm_provider = llm_provider
        self.top_k = top_k

    def _build_contexts(self, doc_ids: list[str]) -> list[ContextChunk]:
        docs = {d.id: d for d in self.db.query(Document).filter(Document.id.in_(doc_ids))}
        contexts = []
        for doc_id in doc_ids:
            doc = docs.get(doc_id)
            if doc is None:
                continue
            contexts.append(
                ContextChunk(
                    doc_id=doc.id,
                    title=doc.title,
                    url=doc.url,
                    source=doc.source,
                    text=doc.text[:CONTEXT_CHARS],
                )
            )
        return contexts

    def answer(self, query: str) -> RagAnswer:
        inference_hits = self.retriever.search(query, top_k=self.top_k)
        vector_hits = self.vector_retriever.search(query, top_k=self.top_k)
        doc_ids = _merge_hit_ids(inference_hits, vector_hits, top_k=self.top_k)

        if not doc_ids:
            return RagAnswer(
                query=query,
                answer="I couldn't find any indexed sources relevant to this question.",
                sources=[],
            )

        contexts = self._build_contexts(doc_ids)
        prompt = build_prompt(query, contexts)
        generated = self.llm_provider.generate(prompt, system=SYSTEM_PROMPT)
        return RagAnswer(query=query, answer=generated, sources=contexts)
