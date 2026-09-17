def test_health_endpoint(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_high_risk_message_returns_explanations(client):
    response = client.post(
        "/api/analyse",
        json={
            "text": (
                "Urgent: your account is suspended. Login at http://bit.ly/verify-now "
                "and enter your password immediately."
            )
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["risk_score"] >= 60
    assert payload["verdict"] in {"Suspicious", "High risk"}
    assert len(payload["signals"]) >= 3


def test_validation_rejects_short_message(client):
    response = client.post("/api/analyse", json={"text": "short"})

    assert response.status_code == 422


def test_analysis_is_added_to_history(client):
    client.post(
        "/api/analyse",
        json={"text": "Please review the normal project meeting agenda for tomorrow morning."},
    )

    response = client.get("/api/history?limit=5")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert "project meeting" in response.json()[0]["preview"]
