import pytest
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from db import engine, SessionLocal, Base
from models import ChuckJoke

@pytest.mark.integration
def test_database_connection_and_crud(db_session):
    """
    Integration test to verify connection to the test PostgreSQL database
    and that basic CRUD operations work with the ChuckJoke model.
    """

    # Test raw connection works by running a simple query
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1

    # Test that tables exist (metadata created in db_session fixture)
    inspector = engine.dialect.get_inspector(engine)
    tables = inspector.get_table_names()
    assert "chuck_jokes" in tables

    # Test CRUD: add a ChuckJoke, commit, and query it back
    joke_text = "Integration test Chuck Norris joke."
    new_joke = ChuckJoke(joke=joke_text)
    db_session.add(new_joke)
    db_session.commit()

    fetched_joke = db_session.query(ChuckJoke).filter_by(joke=joke_text).first()
    assert fetched_joke is not None
    assert fetched_joke.joke == joke_text

    # Cleanup: delete the joke
    db_session.delete(fetched_joke)
    db_session.commit()

    # Confirm deletion
    deleted_joke = db_session.query(ChuckJoke).filter_by(joke=joke_text).first()
    assert deleted_joke is None
