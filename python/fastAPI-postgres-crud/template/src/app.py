import os
import logging
from time import sleep
from fastapi import FastAPI
from sqlalchemy import text
from contextlib import asynccontextmanager

import framework.db
from models.chuck_joke import Base
from api import health, info, sample

# Setup logging before anything else uses it
logger = logging.getLogger(__name__)
if os.getenv("TESTING") != "true":
    from framework.middleware import LoggingMiddleware
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    app_middleware = [LoggingMiddleware]
    otel_enabled = True
else:  # Basic logging when running tests
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    app_middleware = []
    otel_enabled = False

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

# Create FastAPI app
app = FastAPI(lifespan=lifespan)

# Add middleware and instrumentation
if os.getenv("TESTING") != "true":
    for mw in app_middleware:
        app.add_middleware(mw)
    if otel_enabled:
        FastAPIInstrumentor.instrument_app(app)

# Register routes
app.include_router(health.router, tags=["Health"])
app.include_router(info.router, tags=["Info"])
app.include_router(sample.router, tags=["Sample"])
