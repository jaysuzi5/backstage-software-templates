from time import sleep
import os
import logging
from fastapi import FastAPI
from framework.db import init_db, SessionLocal, engine
from models.chuck_joke import Base
from api import health, info, sample
from sqlalchemy.exc import OperationalError
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    max_retries = 5
    retry_delay = 2
    
    if os.getenv("TESTING") != "true":
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting database connection (attempt {attempt + 1}/{max_retries})")
                
                # Initialize database
                init_db()
                
                # Verify connection
                Base.metadata.create_all(bind=engine)
                with SessionLocal() as session:
                    session.execute("SELECT 1")
                
                logger.info("Database connection established successfully")
                break
            except Exception as e:
                logger.error(f"Database connection failed: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error("Max retries reached, failing startup")
                    raise
                sleep(retry_delay)
    yield

app = FastAPI(lifespan=lifespan)

# Register API route modules
app.include_router(health.router, tags=["Health"])
app.include_router(info.router, tags=["Info"])
app.include_router(sample.router, tags=["Sample"])