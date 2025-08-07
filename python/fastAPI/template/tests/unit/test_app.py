from fastapi.testclient import TestClient
from unittest import mock
from sqlalchemy.exc import OperationalError
from src.app import app

def test_lifespan_success(monkeypatch):
    """Test that lifespan completes successfully"""
    monkeypatch.delenv("TESTING", raising=False)

    with mock.patch("src.app.init_db") as mock_init, \
         mock.patch("sqlalchemy.orm.Session.execute") as mock_execute, \
         mock.patch("src.app.engine") as mock_engine, \
         mock.patch("src.app.Base.metadata.create_all") as mock_create_all:

        mock_execute.return_value = None

        with TestClient(app):  # Triggers the app lifespan
            pass

        mock_init.assert_called_once()
        mock_create_all.assert_called_once_with(bind=mock_engine)

def test_lifespan_retries_on_db_failure(monkeypatch):
    """Test that lifespan retries on database connection failures"""
    monkeypatch.delenv("TESTING", raising=False)

    with mock.patch("src.app.init_db") as mock_init, \
         mock.patch("time.sleep") as mock_sleep, \
         mock.patch("sqlalchemy.orm.Session.execute") as mock_execute, \
         mock.patch("src.app.engine") as mock_engine, \
         mock.patch("src.app.Base.metadata.create_all") as mock_create_all:

        # Simulate two failures, then a success
        mock_execute.side_effect = [
            OperationalError("Failed", {}, {}),
            OperationalError("Failed", {}, {}),
            None
        ]

        with TestClient(app):
            pass

        assert mock_init.call_count == 3
        mock_create_all.assert_called_once_with(bind=mock_engine)