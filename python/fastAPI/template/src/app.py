from time import sleep
import os
import logging
from fastapi import FastAPI
import framework.db
from framework.middleware import LoggingMiddleware
from models.chuck_joke import Base
from api import health, info, sample
from sqlalchemy import text
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from contextlib import asynccontextmanager



@asynccontextmanager
async def lifespan(app: FastAPI):
    max_retries = 5
    retry_delay = 2
    
    if os.getenv("TESTING") != "true":
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting database connection (attempt {attempt + 1}/{max_retries})")
                framework.db.init_db()
                Base.metadata.create_all(bind=framework.db.engine)
                with framework.db.SessionLocal() as session:
                    session.execute(text("SELECT 1"))
                        
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
logger = logging.getLogger(__name__)
if os.getenv("TESTING") != "true":
    app.add_middleware(LoggingMiddleware)
    FastAPIInstrumentor.instrument_app(app)
else:  # Basic logging when running tests
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Register API route modules
app.include_router(health.router, tags=["Health"])
app.include_router(info.router, tags=["Info"])
app.include_router(sample.router, tags=["Sample"])