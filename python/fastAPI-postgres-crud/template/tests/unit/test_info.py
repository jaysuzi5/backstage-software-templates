def test_info(client):
    """Test the /info endpoint returns expected keys."""
    response = client.get("/api/v1/${{values.app_name}}/info")
    assert response.status_code == 200
    data = response.json()
    assert "hostname" in data
    assert "env" in data
    assert "app_name" in data
    assert "time" in data
