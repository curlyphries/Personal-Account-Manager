"""Database setup for the Personal Account Manager app.

This module initializes the SQLModel engine and provides a sessionmaker
for database interactions. Error handling ensures that database connection
issues are clearly reported for easier troubleshooting by junior admins.
"""

from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import StaticPool

import logging
import os

# Set up a module-level logger so database issues are captured consistently.
logger = logging.getLogger(__name__)

# Load database URL from environment variable with a sensible default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/app.db")

# Create the engine with sensible defaults for SQLite and other databases
connect_args = {}
engine_kwargs = {"echo": os.getenv("DEBUG", "0") == "1"}

if DATABASE_URL.startswith("sqlite"):
    # Allow usage across threads; StaticPool is required for in-memory DBs.
    connect_args["check_same_thread"] = False
    if DATABASE_URL == "sqlite://":
        engine_kwargs["poolclass"] = StaticPool

engine = create_engine(DATABASE_URL, connect_args=connect_args, **engine_kwargs)


def init_db() -> None:
    """Create database tables.

    Wrapped in try/except to provide clear error messages if initialization
    fails. This helps administrators quickly diagnose configuration issues.
    """
    try:
        SQLModel.metadata.create_all(engine)
    except SQLAlchemyError as exc:
        logger.exception("Database initialization failed")
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
        # Log and then raise to alert callers of the failure.
        logger.exception("Database session error")
        raise RuntimeError("Database session error") from exc
    finally:
        session.close()
