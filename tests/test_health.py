
def test_health_is_fast_and_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["app"] == "CallShield"
