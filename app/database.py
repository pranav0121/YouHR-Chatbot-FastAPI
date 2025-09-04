from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import sys

# Load .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    sys.stderr.write(
        "ERROR: DATABASE_URL is not set. Please create a .env file (see .env.example) and set DATABASE_URL to a PostgreSQL connection string.\n")
    raise RuntimeError("DATABASE_URL not configured")

# Use PostgreSQL for production. If the variable points to sqlite, accept it but warn.
if DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgres://"):
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False
    )
elif DATABASE_URL.startswith("sqlite:"):
    # SQLite configuration (development/fallback)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False, "timeout": 30}
    )
else:
    # Unknown scheme — try to create engine but loudly warn
    sys.stderr.write(
        f"WARNING: DATABASE_URL uses an unrecognized scheme. Attempting to use it anyway: {DATABASE_URL}\n")
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
