from fastapi import FastAPI

app = FastAPI(
    title="CodeRadar",
    description="Information retrieval + RAG system for the technology and software domain",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
