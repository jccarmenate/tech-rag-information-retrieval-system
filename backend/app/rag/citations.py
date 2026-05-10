import re
from dataclasses import dataclass

from app.rag.prompts import ContextChunk

_CITATION_RE = re.compile(r"\[(\d+)\]")


@dataclass
class Citation:
    index: int
    doc_id: str
    title: str
    url: str
    source: str


def extract_citations(answer: str, sources: list[ContextChunk]) -> list[Citation]:
    """Maps the [n] markers actually used in the generated answer back to their source.

    Sources the model never cited are dropped, and unknown indices (a model
    hallucinating [7] when only 5 sources were given) are ignored rather than
    raising, since this only affects a "sources used" list, not correctness.
    """
    cited_indices = sorted({int(m) for m in _CITATION_RE.findall(answer)})
    citations = []
    for index in cited_indices:
        if 1 <= index <= len(sources):
            chunk = sources[index - 1]
            citations.append(
                Citation(
                    index=index,
                    doc_id=chunk.doc_id,
                    title=chunk.title,
                    url=chunk.url,
                    source=chunk.source,
                )
            )
    return citations
