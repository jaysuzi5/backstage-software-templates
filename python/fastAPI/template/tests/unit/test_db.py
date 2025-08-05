import os
import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from importlib import reload
import db  # your actual db.py file


def set_env_vars():
    """Helper function to set environment variables for test DB config."""
    os.environ["POSTGRES_USER"] = "test_user"
    os.environ["POSTGRES_PASSWORD"] = "test_pass"
    os.environ["POSTGRES_HOST"] = "localhost"
    os.environ["POSTGRES_PORT"] = "5432"
    os.environ["POSTGRES_DB"] = "test_db"


def clear_env_vars():
    """Helper function to clear the relevant environment variables."""
    for var in [
        "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST", 
        "POSTGRES_PORT", "POSTGRES_DB"
    ]:
        os.environ.pop(var, None)


@pytest.fixture(autouse=True)
def setup_and_teardown_env():
    """Set up env vars before test and clean after."""
    set_env_vars()
    yield
    clear_env_vars()


def test_database_url_construction():
    """Test that DATABASE_URL is constructed correctly."""
    reload(db)  # re-import to trigger re-evaluation of env vars
    expected = (
        "postgresql+psycopg2://test_user:test_pass@localhost:5432/test_db"
    )
    assert db.DATABASE_URL == expected


def test_engine_creation():
    """Test that SQLAlchemy engine is created."""
    reload(db)
    assert isinstance(db.engine, Engine)


def test_sessionlocal_is_sessionmaker():
    """Test that SessionLocal is a valid sessionmaker."""
    reload(db)
    assert isinstance(db.SessionLocal, sessionmaker)


def test_missing_env_vars_causes_failure(monkeypatch):
    """Test behavior when required environment variables are missing."""
    clear_env_vars()
    monkeypatch.delenv("POSTGRES_USER", raising=False)
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)
    monkeypatch.delenv("POSTGRES_HOST", raising=False)
    monkeypatch.delenv("POSTGRES_PORT", raising=False)
    monkeypatch.delenv("POSTGRES_DB", raising=False)

    with pytest.raises(Exception):
        reload(db)
