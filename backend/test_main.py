import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_read_item():
    response = client.get("/items/123?q=testquery")
    assert response.status_code == 200
    assert response.json() == {"item_id": 123, "q": "testquery"}


def test_soc_test_predict():
    response = client.get("/soc-test-predict/")
    assert response.status_code == 200
    assert "predicted_soc" in response.json()


def test_soh_test_predict():
    response = client.get("/soh-test-predict/")
    assert response.status_code == 200
    assert "predicted_soh" in response.json()


def test_get_battery_data_valid():
    response = client.get("/api/data/05")
    if response.status_code == 200:
        assert isinstance(response.json(), list)
    else:
        assert response.status_code == 404


def test_get_battery_data_invalid():
    response = client.get("/api/data/999")
    assert response.status_code == 404
