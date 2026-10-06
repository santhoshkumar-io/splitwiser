"""Database engine, session factory, and the declarative Base.

`Base` lives here rather than in models.py so that every model module
imports it from one place. Importing it the other way round (models.py
owning Base, database.py importing models) would make the two modules
import each other.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Copy .env.example to .env and fill it in."
    )

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind = engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    """Every model subclasses this; it collects their table definitions
    in `Base.metadata`, which is what create_all() reads."""

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
