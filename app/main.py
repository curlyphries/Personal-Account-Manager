"""Entry point for the Personal Account Manager application."""

from fastapi import FastAPI, HTTPException
from sqlmodel import select
from sqlalchemy.exc import SQLAlchemyError
import logging

from .database import init_db, get_session
from .models import Account

# Configure a module-level logger for consistent debugging messages.
logger = logging.getLogger(__name__)

app = FastAPI(title="Personal Account Manager")


@app.on_event("startup")
def on_startup() -> None:
    """Initialize services when the application starts."""
    init_db()


@app.get("/", summary="Health check")
def read_root() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.get("/accounts", response_model=list[Account])
def list_accounts() -> list[Account]:
    """Return all accounts in the system."""
    with get_session() as session:
        try:
            return session.exec(select(Account)).all()
        except SQLAlchemyError as exc:
            session.rollback()  # Ensure the session is clean for subsequent operations.
            logger.exception("Database error while listing accounts")
            raise HTTPException(
                status_code=500,
                detail="Database error while listing accounts",
            ) from exc


@app.post("/accounts", response_model=Account)
def create_account(account: Account) -> Account:
    """Create a new account with database error handling.

    Errors are logged and surfaced to aid junior admins in troubleshooting.
    """
    with get_session() as session:
        try:
            session.add(account)
            session.commit()
            session.refresh(account)
            return account
        except SQLAlchemyError as exc:
            session.rollback()  # Prevent partial commits on failure.
            logger.exception("Database error while creating an account")
            raise HTTPException(
                status_code=500,
                detail="Database error while creating account",
            ) from exc
