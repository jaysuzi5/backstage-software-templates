import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from framework.db import get_db
from models.chuck_joke import ChuckJoke

router = APIRouter()

@router.get("/api/thursday/v1/sample")
def sample(db: Session = Depends(get_db)):
    """
    Retrieve and store a Chuck Norris joke, and return the 10 most recent jokes.

    This endpoint fetches a random Chuck Norris joke from the external API at 
    https://api.chucknorris.io/jokes/random. If the joke is not already present 
    in the database, it is saved. The response includes the fetched API data and 
    the 10 most recently stored jokes from the local database.

    The endpoint performs the following:
    - Makes a request to the external joke API.
    - Validates the returned data.
    - Stores the joke in the database if it does not already exist.
    - Queries and returns the 10 latest stored jokes (sorted by creation date descending).

    Args:
        db (Session): SQLAlchemy database session injected by FastAPI's dependency 
                      system.

    Returns:
        dict: A dictionary containing:
            - `api_data` (dict): The full response from the external joke API.
            - `jokes` (list): A list of the 10 most recent jokes stored in the database,
              each with fields:
                - `id` (int): Primary key of the joke.
                - `joke` (str): The joke text.
                - `create_date` (str): ISO-formatted timestamp of when the joke was added.

    Raises:
        HTTPException: 
            - 422: If the external API response does not include the expected joke format.
            - 502: If the request to the external API fails (e.g., timeout, bad response).
            - 500: For any other unhandled server error.
    """
    try:
        joke_data = fetch_joke_from_api()
        joke_text = joke_data.get("value")

        if not joke_text:
            raise HTTPException(status_code=422, detail="Invalid joke format from API")

        # Save to DB if not exists
        if not db.query(ChuckJoke).filter_by(joke=joke_text).first():
            new_joke = ChuckJoke(joke=joke_text)
            db.add(new_joke)
            db.commit()
            db.refresh(new_joke)

        # Return latest 10 jokes
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

    except requests.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"External API request failed: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


def fetch_joke_from_api() -> dict:
    """
    Fetch a random joke from the Chuck Norris joke API.

    Sends an HTTP GET request to the official Chuck Norris joke API and returns
    the parsed JSON response. This function is separated for easier testing
    and mocking in unit tests.

    Returns:
        dict: A dictionary representing the JSON response from the API.

    Raises:
        requests.RequestException: If the HTTP request fails or returns a bad status.
    """
    url = "https://api.chucknorris.io/jokes/random"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
