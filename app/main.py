"""Entry point for the Personal Account Manager application."""

from fastapi import FastAPI, HTTPException
from sqlmodel import select

from .database import init_db, get_session
from .models import Account

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
        accounts = session.exec(select(Account)).all()
        return accounts


@app.post("/accounts", response_model=Account)
def create_account(account: Account) -> Account:
    """Create a new account with basic error handling."""
    with get_session() as session:
        try:
            session.add(account)
            session.commit()
            session.refresh(account)
            return account
        except Exception as exc:  # Catch generic issues for clarity
            # Raising an HTTPException ensures the API responds cleanly.
            raise HTTPException(status_code=400, detail=str(exc))
