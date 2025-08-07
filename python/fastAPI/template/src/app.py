# app.py
import os
from time import sleep
from fastapi import FastAPI
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from framework.db import get_engine, get_session_local, init_db
from models.chuck_joke import Base
from api import health, info, sample

@asynccontextmanager
async def lifespan(app: FastAPI):
    max_retries = 5
    retry_delay = 2

    testing = os.getenv("TESTING") == "true"
    engine = get_engine(testing)
    SessionLocal = get_session_local(engine)
    app.state.engine = engine
    app.state.SessionLocal = SessionLocal

    if not testing:
        for attempt in range(max_retries):
            try:
                init_db(engine)
                Base.metadata.create_all(bind=engine)
                with SessionLocal() as session:
                    session.execute("SELECT 1")
                break
            except OperationalError:
                if attempt == max_retries - 1:
                    raise
                sleep(retry_delay)

    yield
    # Optional: clean-up here

app = FastAPI(lifespan=lifespan)
app.include_router(health.router, tags=["Health"])
app.include_router(info.router, tags=["Info"])
app.include_router(sample.router, tags=["Sample"])
