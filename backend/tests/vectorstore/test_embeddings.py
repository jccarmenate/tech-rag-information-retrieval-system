from app.vectorstore.embeddings import EmbeddingModel


def test_encode_returns_one_vector_per_text():
    model = EmbeddingModel()
    vectors = model.encode(["python", "rust"])
    assert len(vectors) == 2
    assert len(vectors[0]) == len(vectors[1])
    assert len(vectors[0]) > 0


def test_encode_empty_list_returns_empty():
    model = EmbeddingModel()
    assert model.encode([]) == []


def test_encode_one_returns_single_vector():
    model = EmbeddingModel()
    vector = model.encode_one("hello world")
    assert isinstance(vector, list)
    assert len(vector) > 0
