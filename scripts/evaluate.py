"""Runs the IR evaluation suite against the frozen sample corpus and prints
a metrics report. Usage: python scripts/evaluate.py [k]
"""

import sys

from app.evaluation.runner import run_evaluation

if __name__ == "__main__":
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    report = run_evaluation(k=k)
    print(f"Evaluated {report.num_queries} queries at k={report.k}")
    print(f"  Precision@{k}: {report.precision_at_k:.3f}")
    print(f"  Recall@{k}:    {report.recall_at_k:.3f}")
    print(f"  MAP:           {report.map:.3f}")
    print(f"  MRR:           {report.mrr:.3f}")
    print(f"  nDCG@{k}:       {report.ndcg_at_k:.3f}")
