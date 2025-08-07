import os
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from typing import Optional, TypeVar, Any

Base = declarative_base()
SessionLocal: Optional[sessionmaker] = None
engine: Optional[Any] = None

def init_db():
    """Initialize the database connection."""
    global SessionLocal, engine
    
    required_keys = {
        "POSTGRES_USER": None,
        "POSTGRES_PASSWORD": None,
        "POSTGRES_HOST": None,
        "POSTGRES_PORT": None,
        "POSTGRES_DB": None
    }

    # Validate and collect environment variables
    missing_vars = []
    for key in required_keys:
        value = os.getenv(key)
        if not value:
            missing_vars.append(key)
        required_keys[key] = value
    
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    DATABASE_URL = (
        f"postgresql+psycopg2://{required_keys['POSTGRES_USER']}:"
        f"{required_keys['POSTGRES_PASSWORD']}@"
        f"{required_keys['POSTGRES_HOST']}:"
        f"{required_keys['POSTGRES_PORT']}/"
        f"{required_keys['POSTGRES_DB']}"
    )

    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600
    )
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

def get_db():
    """Provide a database session for dependency injection."""
    if SessionLocal is None:
        init_db()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()