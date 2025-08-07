from fastapi.testclient import TestClient
from unittest import mock
from sqlalchemy.exc import OperationalError
from src.app import app


def test_lifespan_success(monkeypatch):
    """Test that lifespan completes successfully"""
    monkeypatch.delenv("TESTING", raising=False)

    with mock.patch("src.app.init_db") as mock_init, \
         mock.patch("sqlalchemy.orm.Session.execute") as mock_execute, \
         mock.patch("src.app.engine"), \
         mock.patch("src.app.Base.metadata.create_all") as mock_create_all, \
         mock.patch("src.app.SessionLocal") as mock_sessionlocal:

        # Mock the session context manager
        mock_session = mock.MagicMock()
        mock_session.__enter__.return_value = mock_session
        mock_session.__exit__.return_value = False
        mock_sessionlocal.return_value = mock_session

        mock_execute.return_value = None

        with TestClient(app):  # Triggers the app lifespan
            pass

        mock_init.assert_called_once()
        mock_create_all.assert_called_once()


def test_lifespan_retries_on_db_failure(monkeypatch):
    """Test that lifespan retries on database connection failures"""
    monkeypatch.delenv("TESTING", raising=False)

    with mock.patch("src.app.init_db") as mock_init, \
         mock.patch("time.sleep") as mock_sleep, \
         mock.patch("src.app.engine"), \
         mock.patch("src.app.Base.metadata.create_all"), \
         mock.patch("src.app.SessionLocal") as mock_sessionlocal:

        # Mock the session context manager and its execute method
        mock_session = mock.MagicMock()
        mock_session.__enter__.return_value = mock_session
        mock_session.__exit__.return_value = False

        # Simulate two failures and then a success
        mock_session.execute.side_effect = [
            OperationalError("Failed", {}, {}),
            OperationalError("Failed", {}, {}),
            None
        ]
        mock_sessionlocal.return_value = mock_session

        with TestClient(app):
            pass

        assert mock_init.call_count == 3
