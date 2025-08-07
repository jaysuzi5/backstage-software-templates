"""
Main application entrypoint for the FastAPI service.

This application serves as a backend API that includes health checks, application metadata,
and sample data retrieval endpoints. It is designed with extensibility in mind, allowing
future feature additions and endpoint expansion.

Features:
- FastAPI for API routing and OpenAPI documentation.
- SQLAlchemy for database integration.
- Custom middleware for logging requests and responses.
- OpenTelemetry for distributed tracing and observability.
- Modular routing structure for maintainability.

Modules:
- `health`: Liveness and readiness probes.
- `info`: Application metadata (version, uptime, etc.).
- `sample`: Dynamic or static sample data retrieval (to be extended).

Usage:
Start the application using an ASGI server such as Uvicorn:
    uvicorn app:app --reload

Environment variables and database configuration are managed externally via `.env` files.
"""
from time import sleep
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from framework.middleware import LoggingMiddleware
from framework.db import engine, SessionLocal, init_db 
from models.chuck_joke import Base
from api import health, info, sample  # Import routers
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from contextlib import asynccontextmanager


# Automatically create all database tables defined in models
@asynccontextmanager
async def lifespan(app: FastAPI):
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            init_db()
            Base.metadata.create_all(bind=engine)
            # Test connection
            with SessionLocal() as session:
                session.execute("SELECT 1")
            break
        except OperationalError as e:
            if attempt == max_retries - 1:
                raise
            sleep(retry_delay)
    yield
    
    # Optional: Add any cleanup code here

app = FastAPI(lifespan=lifespan)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Register API route modules
app.include_router(health.router, tags=["Health"])
app.include_router(info.router, tags=["Info"])
app.include_router(sample.router, tags=["Sample"])
