from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.acquisition.service import IngestionResult, get_connectors, ingest_all
from app.core.config import get_settings
from app.db.session import get_db

router = APIRouter(prefix="/api/acquisition", tags=["acquisition"])


@router.post("/refresh", response_model=IngestionResult)
def refresh(db: Annotated[Session, Depends(get_db)], limit_per_source: int = 20) -> IngestionResult:
    settings = get_settings()
    connectors = get_connectors(github_token=settings.github_token)
    return ingest_all(db, connectors=connectors, limit_per_source=limit_per_source)
