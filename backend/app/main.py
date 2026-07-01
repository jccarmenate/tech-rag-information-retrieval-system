from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.acquisition.scheduler import create_scheduler
from app.api.routes import acquisition, feedback, multimodal, rag, search
from app.core.config import get_settings
from app.db.session import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    scheduler = create_scheduler()
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(
    title=settings.app_name,
    description="Information retrieval + RAG system for the technology and software domain",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(acquisition.router)
app.include_router(search.router)
app.include_router(rag.router)
app.include_router(feedback.router)
app.include_router(multimodal.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
