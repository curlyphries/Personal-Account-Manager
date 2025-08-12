"""Database setup for the Personal Account Manager app.

This module initializes the SQLModel engine and provides a sessionmaker
for database interactions. Error handling ensures that database connection
issues are clearly reported for easier troubleshooting by junior admins.
"""

from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.exc import SQLAlchemyError

import os

# Load database URL from environment variable with a sensible default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/app.db")

# Create the engine with echo enabled only in debug scenarios
engine = create_engine(DATABASE_URL, echo=os.getenv("DEBUG", "0") == "1")


def init_db() -> None:
    """Create database tables.

    Wrapped in try/except to provide clear error messages if initialization
    fails. This helps administrators quickly diagnose configuration issues.
    """
    try:
        SQLModel.metadata.create_all(engine)
    except SQLAlchemyError as exc:
        # Raising a RuntimeError surfaces the issue to the app startup while
        # preserving the original exception context for detailed logs.
        raise RuntimeError("Database initialization failed") from exc


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except SQLAlchemyError as exc:
        session.rollback()
        # Rollback is followed by raising to alert callers of the failure.
        raise RuntimeError("Database session error") from exc
    finally:
        session.close()
