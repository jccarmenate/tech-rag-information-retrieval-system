from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.acquisition.service import IngestionResult, ingest_all
from app.db.session import get_db

router = APIRouter(prefix="/api/acquisition", tags=["acquisition"])


@router.post("/refresh", response_model=IngestionResult)
def refresh(limit_per_source: int = 20, db: Session = Depends(get_db)) -> IngestionResult:
    return ingest_all(db, limit_per_source=limit_per_source)
