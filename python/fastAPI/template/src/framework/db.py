import os
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from typing import Optional, TypeVar, Any
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()
SessionLocal: Optional[sessionmaker] = None
engine: Optional[Any] = None

def init_db(database_url: str = None, **engine_kwargs):
    """Initialize the database connection."""
    global SessionLocal, engine
    
    try:
        if database_url is None:
            database_url = os.getenv("DATABASE_URL")
            if database_url is None:
                # Production configuration
                required_keys = {
                    "POSTGRES_USER": None,
                    "POSTGRES_PASSWORD": None,
                    "POSTGRES_HOST": None,
                    "POSTGRES_PORT": None,
                    "POSTGRES_DB": None
                }

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

                database_url = (
                    f"postgresql+psycopg2://{required_keys['POSTGRES_USER']}:"
                    f"{required_keys['POSTGRES_PASSWORD']}@"
                    f"{required_keys['POSTGRES_HOST']}:"
                    f"{required_keys['POSTGRES_PORT']}/"
                    f"{required_keys['POSTGRES_DB']}"
                )

                # Default pool configuration for production
                pool_config = {
                    "pool_pre_ping": True,
                    "pool_size": int(os.getenv("DB_POOL_SIZE", 10)),
                    "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", 20)),
                    "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", 3600))
                }
                pool_config.update(engine_kwargs)
            else:
                pool_config = engine_kwargs
        else:
            # Test configuration
            pool_config = engine_kwargs

        logger.info(f"Initializing database with URL: {database_url.split('@')[0]}...@...")  # Log sanitized URL
        engine = create_engine(database_url, **pool_config)
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

def get_db():
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()