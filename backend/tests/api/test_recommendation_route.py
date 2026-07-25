from app.api.routes import recommendation as recommendation_route
from app.recommendation.recommender import Recommendation


def test_recommendations_returns_hydrated_results(client_with_docs, monkeypatch):
    client, _ = client_with_docs
    monkeypatch.setattr(recommendation_route, "liked_doc_ids", lambda db, user_id: ["doc-1"])
    monkeypatch.setattr(
        recommendation_route,
        "recommend",
        lambda db, store, liked, top_k: [Recommendation(doc_id="doc-1", score=0.8)],
    )

    response = client.get("/api/recommendations", params={"user_id": "alice"})

    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "alice"
    assert body["results"][0]["title"] == "A great Python repo"


def test_recommendations_empty_for_user_with_no_likes(client_with_docs, monkeypatch):
    client, _ = client_with_docs
    monkeypatch.setattr(recommendation_route, "liked_doc_ids", lambda db, user_id: [])
    monkeypatch.setattr(recommendation_route, "recommend", lambda db, store, liked, top_k: [])

    response = client.get("/api/recommendations", params={"user_id": "new_user"})

    assert response.json()["results"] == []
