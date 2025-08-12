"""Entry point for the Personal Account Manager application."""

from fastapi import FastAPI, HTTPException
from sqlmodel import select
from sqlalchemy.exc import SQLAlchemyError
import logging
from datetime import datetime

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


@app.put("/accounts/{account_id}", response_model=Account)
def update_account(account_id: int, account: Account) -> Account:
    """Modify an existing account in the database.

    Returns the updated account or a 404 if the account does not exist.
    """
    with get_session() as session:
        try:
            existing_account = session.get(Account, account_id)
            if existing_account is None:
                raise HTTPException(status_code=404, detail="Account not found")

            # Update mutable fields while keeping audit fields intact.
            existing_account.name = account.name
            existing_account.status = account.status
            existing_account.tags = account.tags
            existing_account.owner = account.owner
            existing_account.updated_at = datetime.utcnow()

            session.add(existing_account)
            session.commit()
            session.refresh(existing_account)
            return existing_account
        except SQLAlchemyError as exc:
            session.rollback()
            logger.exception("Database error while updating an account")
            raise HTTPException(
                status_code=500,
                detail="Database error while updating account",
            ) from exc


@app.delete("/accounts/{account_id}")
def delete_account(account_id: int) -> dict[str, bool]:
    """Remove an account from the system."""
    with get_session() as session:
        try:
            account = session.get(Account, account_id)
            if account is None:
                raise HTTPException(status_code=404, detail="Account not found")
            session.delete(account)
            session.commit()
            return {"ok": True}
        except SQLAlchemyError as exc:
            session.rollback()
            logger.exception("Database error while deleting an account")
            raise HTTPException(
                status_code=500,
                detail="Database error while deleting account",
            ) from exc
