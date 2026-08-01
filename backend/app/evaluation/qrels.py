import json
from dataclasses import dataclass
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "evaluation"
QRELS_PATH = DATA_DIR / "qrels.json"
SAMPLE_CORPUS_PATH = DATA_DIR / "sample_corpus.json"


@dataclass
class QueryJudgment:
    query: str
    relevant_doc_ids: set[str]


def load_qrels(path: Path = QRELS_PATH) -> list[QueryJudgment]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [
        QueryJudgment(query=row["query"], relevant_doc_ids=set(row["relevant_doc_ids"]))
        for row in raw
    ]


def load_sample_corpus(path: Path = SAMPLE_CORPUS_PATH) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))
