from app.rag.citations import extract_citations
from app.rag.prompts import ContextChunk

_SOURCES = [
    ContextChunk(doc_id="a", title="A", url="urlA", source="github", text="..."),
    ContextChunk(doc_id="b", title="B", url="urlB", source="devto", text="..."),
]


def test_extracts_cited_sources_in_order():
    citations = extract_citations("First point [1]. Second point [2].", _SOURCES)
    assert [c.doc_id for c in citations] == ["a", "b"]


def test_deduplicates_repeated_citation_markers():
    citations = extract_citations("Repeated [1] and [1] again.", _SOURCES)
    assert len(citations) == 1


def test_ignores_out_of_range_indices():
    citations = extract_citations("Bogus citation [99].", _SOURCES)
    assert citations == []


def test_no_citations_in_answer_returns_empty_list():
    assert extract_citations("No markers here.", _SOURCES) == []
