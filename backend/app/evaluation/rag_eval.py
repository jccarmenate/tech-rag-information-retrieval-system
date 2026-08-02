import re

from app.rag.llm_providers.base import LLMProvider
from app.rag.prompts import ContextChunk

_CITATION_RE = re.compile(r"\[(\d+)\]")

_JUDGE_SYSTEM_PROMPT = (
    "You are a strict evaluator. Given numbered sources and a generated answer, "
    "rate how well the answer is supported by the sources alone, from 1 (mostly "
    "unsupported or contradicted by the sources) to 5 (every claim is directly "
    "supported by a source). Respond with only a single digit from 1 to 5, nothing else."
)


def citation_coverage(answer: str, num_sources: int) -> float:
    """A cheap, LLM-free faithfulness proxy: what fraction of the sources
    handed to the model did it actually cite? Doesn't verify the citations
    are *correct*, only that the answer engaged with the given evidence.
    """
    if num_sources == 0:
        return 0.0
    cited = {int(m) for m in _CITATION_RE.findall(answer)}
    valid_cited = {i for i in cited if 1 <= i <= num_sources}
    return len(valid_cited) / num_sources


def judge_faithfulness(
    llm_provider: LLMProvider, query: str, answer: str, sources: list[ContextChunk]
) -> int | None:
    """LLM-as-judge: reuses the same LLMProvider abstraction the RAG pipeline
    uses to generate answers, so this works offline with Ollama exactly the
    same way it would with Anthropic.
    """
    sources_block = "\n\n".join(
        f"[{i}] {chunk.title}\n{chunk.text}" for i, chunk in enumerate(sources, 1)
    )
    prompt = f"Sources:\n{sources_block}\n\nQuestion: {query}\n\nAnswer: {answer}\n\nScore (1-5):"
    response = llm_provider.generate(prompt, system=_JUDGE_SYSTEM_PROMPT)
    match = re.search(r"[1-5]", response)
    return int(match.group()) if match else None
