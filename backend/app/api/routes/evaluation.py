from fastapi import APIRouter

from app.evaluation.runner import EvaluationReport, run_evaluation

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])


@router.post("/run", response_model=EvaluationReport)
def run(k: int = 5) -> EvaluationReport:
    return run_evaluation(k=k)
