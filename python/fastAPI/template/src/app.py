from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
import datetime
import requests
import socket
from sqlalchemy.orm import Session
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from db import SessionLocal, engine
from models import Base, WeatherCurrent
from middleware import LoggingMiddleware

# Initialize DB models
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(LoggingMiddleware)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/${{values.app_name}}/v1/sample")
def sample(db: Session = Depends(get_db)):
    response = requests.get('https://api.chucknorris.io/jokes/random')

    latest_weather = (
        db.query(WeatherCurrent.collection_time, WeatherCurrent.temperature)
        .order_by(WeatherCurrent.collection_time.desc())
        .limit(10)
        .all()
    )

    return {
        "api_data": response.text,
        "weather": [
            {
                "collection_time": w.collection_time.isoformat(),
                "temperature": w.temperature
            } for w in latest_weather
        ]
    }

@app.get("/api/${{values.app_name}}/v1/info")
def info():
    return {
        'hostname': socket.gethostname(),
        'env': '${{values.app_env}}',
        'app_name': '${{values.app_name}}',
        'time': datetime.datetime.now().strftime("%I:%M:%S %p on %Y-%m-%d")
    }

@app.get("/api/${{values.app_name}}/v1/health")
def health():
    return {"status": "UP"}
