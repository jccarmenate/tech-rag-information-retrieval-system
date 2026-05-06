from dataclasses import dataclass

SYSTEM_PROMPT = (
    "You are CodeRadar's assistant, answering questions about software and technology "
    "using only the numbered sources provided below. Cite every claim with its source "
    "number in square brackets, e.g. [1]. If the sources do not contain enough "
    "information to answer, say so plainly instead of guessing."
)


@dataclass
class ContextChunk:
    doc_id: str
    title: str
    url: str
    source: str
    text: str


def build_prompt(query: str, contexts: list[ContextChunk]) -> str:
    sources = "\n\n".join(
        f"[{i}] {chunk.title} ({chunk.source})\n{chunk.text}" for i, chunk in enumerate(contexts, 1)
    )
    return (
        f"Sources:\n{sources}\n\n"
        f"Question: {query}\n\n"
        "Answer the question using only the sources above, citing them as [1], [2], etc."
    )
