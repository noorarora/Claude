from app.rag import PhishingRAG


def test_retrieval_prioritises_clicked_link_guidance():
    rag = PhishingRAG()

    results = rag.retrieve(
        "I clicked a suspicious link and installed software. What should I do?",
        top_k=2,
    )

    assert len(results) == 2
    assert results[0]["id"] == "clicked-link"
    assert results[0]["score"] > 0


def test_rag_endpoint_returns_grounded_sources_without_api_key(client, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_MODEL", raising=False)

    response = client.post(
        "/api/rag",
        json={
            "query": "I entered my password into a suspicious login page. What now?",
            "top_k": 3,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["generated_by"] == "retrieval-fallback"
    assert len(payload["sources"]) == 3
    assert any(source["id"] == "credentials-exposed" for source in payload["sources"])
    assert "definitive verdict" in payload["answer"]


def test_rag_endpoint_validates_top_k(client):
    response = client.post(
        "/api/rag",
        json={"query": "How should I verify this message?", "top_k": 9},
    )

    assert response.status_code == 422


def test_unrelated_query_has_no_sources_and_skips_generation(monkeypatch):
    rag = PhishingRAG()

    def unexpected_generation(*args):
        raise AssertionError("Generation must not run without evidence")

    monkeypatch.setattr(rag, "_generate_with_claude", unexpected_generation)
    answer, sources, mode = rag.answer("zxqv blorptastic")
    assert sources == []
    assert mode == "no-evidence"
    assert "No relevant guidance" in answer


def test_unrelated_query_endpoint(client):
    response = client.post("/api/rag", json={"query": "zxqv blorptastic"})
    assert response.status_code == 200
    assert response.json()["sources"] == []
    assert response.json()["generated_by"] == "no-evidence"


def test_retrieval_excludes_zero_overlap_documents(tmp_path):
    import json

    path = tmp_path / "knowledge.json"
    path.write_text(json.dumps([
        {"id": "a", "title": "Passwords", "content": "credentials password"},
        {"id": "b", "title": "Bananas", "content": "orchard fruit"},
    ]))
    results = PhishingRAG(path).retrieve("password", top_k=3)
    assert [source["id"] for source in results] == ["a"]
