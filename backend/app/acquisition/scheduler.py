import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.acquisition.service import IngestionResult, get_connectors, ingest_all
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.indexing.build_index import build_and_save
from app.retrieval.service import reset_retriever_cache

logger = logging.getLogger(__name__)


def run_once() -> IngestionResult:
    settings = get_settings()
    db = SessionLocal()
    try:
        connectors = get_connectors(github_token=settings.github_token)
        result = ingest_all(
            db, connectors=connectors, limit_per_source=settings.acquisition_limit_per_source
        )
        build_and_save(db)
        reset_retriever_cache()
        logger.info("acquisition run: %s", result)
        return result
    finally:
        db.close()


def create_scheduler() -> BackgroundScheduler:
    settings = get_settings()
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        run_once,
        "interval",
        hours=settings.acquisition_interval_hours,
        id="acquisition_refresh",
    )
    return scheduler
