def chunk_text(text: str, chunk_size: int = 200, overlap: int = 40) -> list[str]:
    """Splits text into overlapping word windows.

    Sentence embedding models such as all-MiniLM-L6-v2 silently truncate
    input beyond ~256 tokens, so long documents (e.g. arXiv abstracts plus
    GitHub READMEs) would otherwise lose most of their content. Chunking
    keeps each embedded piece within that budget while the overlap avoids
    cutting a relevant passage exactly at a chunk boundary.
    """
    words = text.split()
    if len(words) <= chunk_size:
        return [text] if words else []

    step = chunk_size - overlap
    chunks = []
    for start in range(0, len(words), step):
        chunk = words[start : start + chunk_size]
        if not chunk:
            break
        chunks.append(" ".join(chunk))
        if start + chunk_size >= len(words):
            break
    return chunks
