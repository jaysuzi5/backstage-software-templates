import requests
from fastapi import APIRouter, Depends, HTTPException 
from sqlalchemy.orm import Session
from framework.db import get_db
from models.chuck_joke import ChuckJoke

router = APIRouter()


@router.get("/api/${{values.app_name}}/v1/sample")
def sample(db: Session = Depends(get_db)):
    try:
        response = requests.get('https://api.chucknorris.io/jokes/random')
        response.raise_for_status()
        joke_data = response.json()
        
        # Validate response format
        if "value" not in joke_data:
            raise HTTPException(status_code=422, detail="Invalid joke format from API")
            
        joke_text = joke_data["value"]

        # Check if joke exists in DB
        exists = db.query(ChuckJoke).filter_by(joke=joke_text).first()
        if not exists:
            new_joke = ChuckJoke(joke=joke_text)
            db.add(new_joke)
            db.commit()
            db.refresh(new_joke)

        # Get latest 10 jokes
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
        raise  # Let fastapi handle the exception, specifically the 422 that we raised    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )