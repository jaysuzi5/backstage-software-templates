import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from framework.db import Base, get_db
from app import app


# Set testing environment for all tests
os.environ["TESTING"] = "true"

@pytest.fixture(scope="session")
def test_engine():
    """Creates a shared in-memory SQLite engine for all tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    # Create tables once for the session
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_engine):
    """Creates a fresh database session with nested transaction rollback."""
    connection = test_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    db = Session()

    db.begin_nested()
    yield db

    db.rollback()
    db.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session, monkeypatch, test_engine):
    """Provides a test client that uses the in-memory DB and patched engine/session."""
    
    # Override get_engine and get_session_local
    from framework import db as db_module

    monkeypatch.setattr(db_module, "get_engine", lambda: test_engine)
    monkeypatch.setattr(db_module, "get_session_local", lambda: lambda: db_session)

    # Also override FastAPI dependency injection
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_joke_response():
    return {
        "categories": [],
        "created_at": "2020-01-05 13:42:22.980058",
        "icon_url": "https://api.chucknorris.io/img/avatar/chuck-norris.png",
        "id": "abc123",
        "updated_at": "2020-01-05 13:42:22.980058",
        "url": "https://api.chucknorris.io/jokes/abc123",
        "value": "Chuck Norris can divide by zero."
    }
