import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app
from models import ChuckJoke
from datetime import datetime

@pytest.fixture
def client():
    """Returns a test client with the app including middleware and DB."""
    with TestClient(app) as c:
        yield c


@pytest.mark.integration
def test_info_endpoint(client):
    """Test the /info endpoint returns expected keys and values."""
    response = client.get("/api/${{values.app_name}}/v1/info")
    assert response.status_code == 200
    json_data = response.json()

    # Basic expected keys
    assert "hostname" in json_data
    assert "env" in json_data
    assert "app_name" in json_data
    assert "time" in json_data

    # Check env and app_name match placeholders (adjust if dynamic)
    assert json_data["env"] == "${{values.app_env}}"
    assert json_data["app_name"] == "${{values.app_name}}"
