import os
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()
SessionLocal = None
engine = None

def init_db():
    global SessionLocal, engine
    required_keys = [
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
    ]

    for key in required_keys:
        value = os.getenv(key)
        if not value:
            raise EnvironmentError(f"Missing required environment variable: {key}")
        if key == "POSTGRES_USER": POSTGRES_USER = value
        elif key == "POSTGRES_PASSWORD": POSTGRES_PASSWORD = value
        elif key == "POSTGRES_HOST": POSTGRES_HOST = value
        elif key == "POSTGRES_PORT": POSTGRES_PORT  = value
        elif key == "POSTGRES_DB": POSTGRES_DB  = value


    DATABASE_URL = (
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)