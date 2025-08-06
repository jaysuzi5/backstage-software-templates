import requests
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from framework.db import SessionLocal
from models.chuck_joke import ChuckJoke


router = APIRouter()

def get_db():
    """
    Dependency that provides a SQLAlchemy database session.
    Closes the session when the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api/${{values.app_name}}/v1/sample")
def sample(db: Session = Depends(get_db)):
    """
    Fetches a random Chuck Norris joke from an external API, 
    stores it in the local database if it doesn't already exist, 
    and returns both the fetched joke and the 10 most recent jokes stored.

    Parameters:
        db (Session): SQLAlchemy session injected by FastAPI's Depends.

    Returns:
        dict: JSON response containing:
            - 'api_data': the full JSON from the external Chuck Norris API.
            - 'jokes': a list of the 10 most recent jokes stored locally.
    """
    response = requests.get('https://api.chucknorris.io/jokes/random')
    joke_data = response.json()
    joke_text = joke_data.get("value")

    exists = db.query(ChuckJoke).filter_by(joke=joke_text).first()
    if not exists:
        new_joke = ChuckJoke(joke=joke_text)
        db.add(new_joke)
        db.commit()

    latest_jokes = (
        db.query(ChuckJoke)
        .order_by(ChuckJoke.create_date.desc())
        .limit(10)
        .all()
    )

    return {
        "api_data": joke_data,
        "jokes": [
            {
                "id": j.id,
                "joke": j.joke,
                "create_date": j.create_date.isoformat()
            } for j in latest_jokes
        ]
    }
