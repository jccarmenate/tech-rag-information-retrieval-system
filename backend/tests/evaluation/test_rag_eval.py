from app.evaluation.rag_eval import citation_coverage, judge_faithfulness
from app.rag.prompts import ContextChunk

_SOURCES = [
    ContextChunk(doc_id="a", title="A", url="urlA", source="github", text="..."),
    ContextChunk(doc_id="b", title="B", url="urlB", source="devto", text="..."),
]


def test_citation_coverage_with_no_sources_is_zero():
    assert citation_coverage("some answer", num_sources=0) == 0.0


def test_citation_coverage_counts_distinct_valid_citations():
    assert citation_coverage("Uses [1] and also [1] plus [2].", num_sources=2) == 1.0


def test_citation_coverage_ignores_out_of_range_citations():
    assert citation_coverage("Only cites [1] and a bogus [9].", num_sources=2) == 0.5


def test_citation_coverage_with_no_citations_is_zero():
    assert citation_coverage("No markers here.", num_sources=2) == 0.0


class _FakeLLM:
    def __init__(self, response: str) -> None:
        self.response = response

    def generate(self, prompt: str, system: str | None = None) -> str:
        return self.response


def test_judge_faithfulness_parses_score_from_response():
    score = judge_faithfulness(_FakeLLM("4"), "query", "answer [1]", _SOURCES)
    assert score == 4


def test_judge_faithfulness_extracts_digit_from_verbose_response():
    score = judge_faithfulness(_FakeLLM("I would rate this a 3 out of 5."), "q", "a", _SOURCES)
    assert score == 3


def test_judge_faithfulness_returns_none_when_unparseable():
    score = judge_faithfulness(_FakeLLM("not a number"), "q", "a", _SOURCES)
    assert score is None
