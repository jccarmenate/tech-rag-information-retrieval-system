from app.retrieval.base import RetrievalResult
from app.vectorstore.chroma_store import ChromaStore


def build_user_profile(store: ChromaStore, liked_doc_ids: list[str]) -> list[float] | None:
    """Averages the embeddings of the documents a user has liked into one
    profile vector. Returns None for a cold-start user with no likes yet.
    """
    vectors = [
        vector
        for doc_id in liked_doc_ids
        if (vector := store.get_document_embedding(doc_id)) is not None
    ]
    if not vectors:
        return None

    dims = len(vectors[0])
    return [sum(v[i] for v in vectors) / len(vectors) for i in range(dims)]


def recommend_content_based(
    store: ChromaStore, liked_doc_ids: list[str], top_k: int = 10
) -> list[RetrievalResult]:
    profile = build_user_profile(store, liked_doc_ids)
    if profile is None:
        return []

    already_liked = set(liked_doc_ids)
    hits = store.query_by_vector(profile, top_k=top_k + len(already_liked))
    recommendations = [h for h in hits if h.doc_id not in already_liked]
    return [RetrievalResult(doc_id=h.doc_id, score=h.similarity) for h in recommendations[:top_k]]
