from fastapi.testclient import TestClient
from unittest import mock
from sqlalchemy.exc import OperationalError
from src.app import app


def test_lifespan_success(monkeypatch):
    """Test that lifespan completes successfully"""
    monkeypatch.delenv("TESTING", raising=False)

    with mock.patch("framework.db.get_engine") as mock_get_engine, \
         mock.patch("framework.db.get_session_local") as mock_get_session_local, \
         mock.patch("framework.db.init_db") as mock_init_db, \
         mock.patch("models.chuck_joke.Base.metadata.create_all") as mock_create_all:

        # Setup mock engine and session
        mock_engine = mock.MagicMock()
        mock_session = mock.MagicMock()
        mock_session.__enter__.return_value = mock_session
        mock_session.__exit__.return_value = False

        mock_get_engine.return_value = mock_engine
        mock_get_session_local.return_value = lambda: mock_session
        mock_session.execute.return_value = None

        with TestClient(app):  # Triggers lifespan
            pass

        mock_init_db.assert_called_once()
        mock_create_all.assert_called_once_with(bind=mock_engine)
        mock_session.execute.assert_called_once_with("SELECT 1")


def test_lifespan_retries_on_db_failure(monkeypatch):
    """Test that lifespan retries on database connection failures"""
    monkeypatch.delenv("TESTING", raising=False)

    with mock.patch("framework.db.get_engine") as mock_get_engine, \
         mock.patch("framework.db.get_session_local") as mock_get_session_local, \
         mock.patch("framework.db.init_db") as mock_init_db, \
         mock.patch("models.chuck_joke.Base.metadata.create_all"), \
         mock.patch("time.sleep") as mock_sleep:

        # Setup mock engine and session
        mock_engine = mock.MagicMock()
        mock_session = mock.MagicMock()
        mock_session.__enter__.return_value = mock_session
        mock_session.__exit__.return_value = False

        mock_get_engine.return_value = mock_engine
        mock_get_session_local.return_value = lambda: mock_session

        # Simulate OperationalError twice, then success
        mock_session.execute.side_effect = [
            OperationalError("Failed", {}, {}),
            OperationalError("Failed", {}, {}),
            None
        ]

        with TestClient(app):
            pass

        assert mock_init_db.call_count == 3
        assert mock_session.execute.call_count == 3
        assert mock_sleep.call_count == 2
