from unittest.mock import patch
import pytest

mock_joke_response = {
    "categories": [],
    "created_at": "2020-01-05 13:42:22.980058",
    "icon_url": "https://api.chucknorris.io/img/avatar/chuck-norris.png",
    "id": "abc123",
    "updated_at": "2020-01-05 13:42:22.980058",
    "url": "https://api.chucknorris.io/jokes/abc123",
    "value": "Chuck Norris can divide by zero."
}

@pytest.fixture(autouse=True)
def mock_requests():
    with patch('requests.get') as mock_get:
        yield mock_get

def test_sample_inserts_new_joke(mock_requests, client, db_session):
    """Test that /sample inserts a new joke if it's not already in DB."""
    mock_requests.return_value.json.return_value = mock_joke_response

    response = client.get("/api/thursday/v1/sample")
    assert response.status_code == 200
    data = response.json()
    assert "Chuck Norris can divide by zero." in [j["joke"] for j in data["jokes"]]
    assert len(data["jokes"]) == 1

def test_sample_does_not_duplicate_jokes(mock_requests, client, db_session):
    """Test that /sample does not insert duplicate jokes."""
    mock_requests.return_value.json.return_value = mock_joke_response

    # First call
    response1 = client.get("/api/thursday/v1/sample")
    assert response1.status_code == 200

    # Second call with same joke
    response2 = client.get("/api/thursday/v1/sample")
    assert response2.status_code == 200

    jokes = response2.json()["jokes"]
    assert len(jokes) == 1  # still only one unique joke

def test_sample_returns_latest_10_jokes(mock_requests, client, db_session):
    """Test that only the 10 latest jokes are returned."""
    for i in range(12):
        mock_requests.return_value.json.return_value = {
            **mock_joke_response,
            "id": f"joke-{i}",
            "value": f"Joke #{i}"
        }
        client.get("/api/thursday/v1/sample")

    response = client.get("/api/thursday/v1/sample")
    jokes = response.json()["jokes"]
    assert len(jokes) == 10
    # Verify ordering (newest first)
    assert jokes[0]["joke"] == "Joke #11"
    assert jokes[-1]["joke"] == "Joke #2"


def test_sample_handles_api_failure(mock_requests, client):
    """Test API failure handling"""
    mock_requests.side_effect = Exception("API Error")
    response = client.get("/api/thursday/v1/sample")
    assert response.status_code == 500
    assert "API Error" in response.json()["detail"]


def test_sample_handles_invalid_joke(mock_requests, client):
    """Test handling of invalid joke format"""
    mock_requests.return_value.json.return_value = {"invalid": "data"}
    response = client.get("/api/thursday/v1/sample")
    assert response.status_code == 422  # Unprocessable Entity        