import pytest
from unittest.mock import patch, MagicMock
from models.chuck_joke import ChuckJoke


@pytest.fixture(autouse=True)
def mock_requests():
    """Automatically patch `requests.get` in all tests."""
    with patch("sample.fetch_joke_from_api") as mock_fetch:
        yield mock_fetch


def test_sample_inserts_new_joke(mock_requests, client, db_session, mock_joke_response):
    """Test that /sample inserts a new joke and verifies DB state"""
    mock_requests.return_value = mock_joke_response

    # Call API
    response = client.get("/api/thursday/v1/sample")
    assert response.status_code == 200
    data = response.json()

    # Check if joke appears in response
    assert "Chuck Norris can divide by zero." in [j["joke"] for j in data["jokes"]]
    assert db_session.query(ChuckJoke).count() == 1


def test_sample_does_not_duplicate_jokes(mock_requests, client, db_session, mock_joke_response):
    """Test that duplicate jokes are not inserted into the database"""
    mock_requests.return_value = mock_joke_response

    # First call inserts joke
    client.get("/api/thursday/v1/sample")
    assert db_session.query(ChuckJoke).count() == 1

    # Second call should not insert again
    response = client.get("/api/thursday/v1/sample")
    assert db_session.query(ChuckJoke).count() == 1
    assert len(response.json()["jokes"]) == 1


def test_sample_returns_latest_10_jokes(mock_requests, client, mock_joke_response):
    """Test that only the 10 most recent jokes are returned, in correct order"""
    for i in range(12):
        mock_requests.return_value = {
            **mock_joke_response,
            "id": f"joke-{i}",
            "value": f"Joke #{i}"
        }
        client.get("/api/thursday/v1/sample")

    # Final call returns latest 10
    response = client.get("/api/thursday/v1/sample")
    jokes = response.json()["jokes"]

    assert len(jokes) == 10
    expected = [f"Joke #{i}" for i in range(11, 1, -1)]
    assert [j["joke"] for j in jokes] == expected


def test_sample_handles_api_failure(mock_requests, client):
    """Test that a failure in API call is handled gracefully with a 500 error"""
    mock_requests.side_effect = Exception("API Error")
    
    response = client.get("/api/thursday/v1/sample")
    assert response.status_code == 500
    assert "API Error" in response.json()["detail"]


def test_sample_handles_invalid_joke(mock_requests, client):
    """Test that invalid joke structure triggers 422 error"""
    mock_requests.return_value = {"invalid": "data"}

    response = client.get("/api/thursday/v1/sample")
    assert response.status_code == 422
    assert "Invalid joke format" in response.json()["detail"]
