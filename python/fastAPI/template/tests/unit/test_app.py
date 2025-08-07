from unittest import mock
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError
from app import app 

def test_lifespan_success():
    """Test that lifespan completes successfully"""
    with mock.patch('app.init_db') as mock_init, \
         mock.patch('sqlalchemy.orm.Session.execute') as mock_execute:
        
        mock_execute.return_value = None

        with TestClient(app):  # This triggers the app lifespan
            pass

        mock_init.assert_called_once()


def test_lifespan_retries_on_db_failure():
    """Test that lifespan retries on database connection failures"""
    with mock.patch('app.init_db') as mock_init, \
         mock.patch('time.sleep') as mock_sleep, \
         mock.patch('sqlalchemy.orm.Session.execute') as mock_execute:

        # Simulate DB connection failure twice, then success
        mock_execute.side_effect = [
            OperationalError("Failed", {}, {}),
            OperationalError("Failed", {}, {}),
            None
        ]

        with TestClient(app):
            pass

        assert mock_init.call_count == 3
