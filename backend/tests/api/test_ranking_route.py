from app.ranking.service import reset_ranking_cache


def test_ranking_model_reports_prior_before_any_votes(client_with_docs):
    client, _ = client_with_docs
    reset_ranking_cache()

    body = client.get("/api/ranking/model").json()

    assert body["trained"] is False
    assert body["n_examples"] == 0
    assert body["weights"] == body["prior_weights"]


def test_feedback_with_relevance_becomes_a_training_example(client_with_docs):
    client, _ = client_with_docs
    reset_ranking_cache()

    client.post(
        "/api/feedback",
        json={"query": "python", "doc_id": "doc-1", "vote": 1, "relevance": 0.7},
    )

    assert client.get("/api/ranking/model").json()["n_examples"] == 1
