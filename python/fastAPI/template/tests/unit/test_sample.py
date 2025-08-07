import pytest
from unittest.mock import patch
from models.chuck_joke import ChuckJoke

@pytest.fixture(autouse=True)
def mock_requests():
    with patch('requests.get') as mock_get:
        yield mock_get


def test_sample_inserts_new_joke(mock_requests, client, db_session):
    """Test that /sample inserts a new joke and verifies DB state"""
    mock_requests.return_value.json.return_value = {
        "id": "test123",
        "value": "Chuck Norris can divide by zero.",
        "created_at": "2020-01-01T00:00:00.000Z"
    }
    
    # Test API response
    response = client.get("/api/thursday/v1/sample")
    assert response.status_code == 200
    data = response.json()
    assert "Chuck Norris can divide by zero." in [j["joke"] for j in data["jokes"]]
    assert len(data["jokes"]) == 1
    
    # Verify mock and database
    mock_requests.assert_called_once_with('https://api.chucknorris.io/jokes/random')
    assert db_session.query(ChuckJoke).count() == 1
    joke = db_session.query(ChuckJoke).first()
    assert joke.joke == "Chuck Norris can divide by zero."

# def test_sample_inserts_new_joke(mock_requests, client, db_session, mock_joke_response):
#     """Test that /sample inserts a new joke and verifies DB state"""
#     mock_requests.return_value.json.return_value = mock_joke_response
    
#     # Test API response
#     response = client.get("/api/thursday/v1/sample")
#     assert response.status_code == 200
#     data = response.json()
#     assert "Chuck Norris can divide by zero." in [j["joke"] for j in data["jokes"]]
#     assert len(data["jokes"]) == 1
    
#     # Verify mock and database
#     mock_requests.assert_called_once_with('https://api.chucknorris.io/jokes/random')
#     assert db_session.query(ChuckJoke).count() == 1

# def test_sample_does_not_duplicate_jokes(mock_requests, client, db_session, mock_joke_response):
#     """Test duplicate prevention with both API and DB checks"""
#     mock_requests.return_value.json.return_value = mock_joke_response

#     # First call
#     client.get("/api/thursday/v1/sample")
#     assert db_session.query(ChuckJoke).count() == 1
    
#     # Second call
#     response = client.get("/api/thursday/v1/sample")
#     jokes = response.json()["jokes"]
    
#     # Verify both API response and DB state
#     assert len(jokes) == 1
#     assert db_session.query(ChuckJoke).count() == 1

# def test_sample_returns_latest_10_jokes(mock_requests, client, mock_joke_response):
#     """Test joke ordering and limiting"""
#     for i in range(12):
#         mock_requests.return_value.json.return_value = {
#             **mock_joke_response,
#             "id": f"joke-{i}",
#             "value": f"Joke #{i}"
#         }
#         client.get("/api/thursday/v1/sample")

#     response = client.get("/api/thursday/v1/sample")
#     jokes = response.json()["jokes"]
    
#     # Verify exact ordering and count
#     assert len(jokes) == 10
#     assert [j["joke"] for j in jokes] == [f"Joke #{i}" for i in range(11, 1, -1)]

# def test_sample_handles_api_failure(mock_requests, client):
#     """Test API failure handling"""
#     mock_requests.side_effect = Exception("API Error")
#     response = client.get("/api/thursday/v1/sample")
#     assert response.status_code == 500
#     assert "API Error" in response.json()["detail"]
#     mock_requests.assert_called_once_with('https://api.chucknorris.io/jokes/random')

# def test_sample_handles_invalid_joke(mock_requests, client):
#     """Test invalid response handling"""
#     mock_requests.return_value.json.return_value = {"invalid": "data"}
#     response = client.get("/api/thursday/v1/sample")
#     assert response.status_code == 422
#     mock_requests.assert_called_once_with('https://api.chucknorris.io/jokes/random')