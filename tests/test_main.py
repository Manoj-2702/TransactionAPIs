import pytest
from fastapi.testclient import TestClient
from src.server.app import app  # Adjust import according to your project structure

@pytest.fixture(scope="module")
def test_client():
    client = TestClient(app)
    return client

def test_read_main(test_client):
    response = test_client.get("/")
    assert response.status_code == 200

def test_start_cron(test_client):
    response = test_client.post("/cron/start", headers={"access_token": "valid_api_key"})
    assert response.status_code == 200

def test_stop_cron(test_client):
    response = test_client.post("/cron/stop", headers={"access_token": "valid_api_key"})
    assert response.status_code == 200

def test_create_transaction(test_client):
    transaction_data = {
        "amount": 100.0,
        "sender_id": "1",
        "destination_id": "2",
        "type": "WITHDRAW",
        "currency": "USD",
        "country": "US"
    }
    response = test_client.post("/create_transactions", json=transaction_data, headers={"access_token": "valid_api_key"})
    assert response.status_code == 200

def test_get_transaction_summary(test_client):
    params = {
        "start_date": "2023-01-01T00:00:00Z",
        "end_date": "2023-12-31T23:59:59Z"
    }
    response = test_client.get("/transactions/summary", params=params, headers={"access_token": "valid_api_key"})
    assert response.status_code == 200

def test_get_total_transaction_amount(test_client):
    params = {
        "start_date": "2023-01-01T00:00:00Z",
        "end_date": "2023-12-31T23:59:59Z"
    }
    response = test_client.get("/transactions/total_amount", params=params, headers={"access_token": "valid_api_key"})
    assert response.status_code == 200
