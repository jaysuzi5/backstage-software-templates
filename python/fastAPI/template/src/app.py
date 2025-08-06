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

from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from framework.middleware import LoggingMiddleware
from framework.db import engine
from python.fastAPI.template.src.models.chuck_joke import Base
from api import health, info, sample  # Import routers

# Initialize the FastAPI app instance
app = FastAPI(
    title="Chuck Norris Joke Service",
    description="A microservice to provide Chuck Norris jokes and system health/info endpoints.",
    version="1.0.0"
)

# Register custom request/response logging middleware
app.add_middleware(LoggingMiddleware)

# Enable OpenTelemetry tracing for the app
FastAPIInstrumentor.instrument_app(app)

# Automatically create all database tables defined in models
Base.metadata.create_all(bind=engine)

# Register API route modules
app.include_router(health.router, tags=["Health"])
app.include_router(info.router, tags=["Info"])
app.include_router(sample.router, tags=["Sample"])
