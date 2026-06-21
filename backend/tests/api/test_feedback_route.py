def test_submit_feedback_persists_vote(client_with_docs):
    client, session = client_with_docs

    response = client.post("/api/feedback", json={"query": "python", "doc_id": "doc-1", "vote": 1})

    assert response.status_code == 200
    body = response.json()
    assert body["doc_id"] == "doc-1"
    assert body["vote"] == 1


def test_submit_feedback_rejects_invalid_vote(client_with_docs):
    client, _ = client_with_docs

    response = client.post("/api/feedback", json={"query": "python", "doc_id": "doc-1", "vote": 2})

    assert response.status_code == 422
