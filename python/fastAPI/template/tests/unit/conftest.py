import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from framework.db import Base, init_db, get_db
from app import app

# Set testing environment
os.environ["TESTING"] = "true"

# Initialize test database once per session
@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    init_db("sqlite:///:memory:")  # Explicitly initialize with test URL
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(test_engine):
    """Creates a fresh database session for each test"""
    connection = test_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    db = Session()
    
    yield db
    
    db.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.rollback()
    
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