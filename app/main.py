"""Entry point for the Personal Account Manager application."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select
from sqlalchemy.exc import SQLAlchemyError
import logging
from datetime import datetime

from .database import init_db, get_session
from .models import Account, Task

# Configure a module-level logger for consistent debugging messages.
logger = logging.getLogger(__name__)

app = FastAPI(title="Personal Account Manager")

# Configure Jinja2 template loader for the simple web interface.
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
def on_startup() -> None:
    """Initialize services when the application starts."""
    init_db()


@app.get("/", summary="Health check")
def read_root() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.get("/ui", response_class=HTMLResponse, summary="Web interface")
def render_ui(request: Request) -> HTMLResponse:
    """Serve the HTML interface for account management."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse, summary="Application dashboard")
def render_dashboard(request: Request) -> HTMLResponse:
    """Render the dashboard page with basic error handling for transparency."""
    try:
        return templates.TemplateResponse("dashboard.html", {"request": request})
    except Exception as exc:  # Broad except to log unexpected template errors
        logger.exception("Error rendering dashboard")
        raise HTTPException(status_code=500, detail="Error loading dashboard") from exc


@app.get("/tasks-ui", response_class=HTMLResponse, summary="Task management interface")
def render_tasks_ui(request: Request) -> HTMLResponse:
    """Serve the HTML interface for basic task management."""
    try:
        return templates.TemplateResponse("tasks.html", {"request": request})
    except Exception as exc:  # Broad except to log unexpected template errors
        logger.exception("Error rendering tasks page")
        raise HTTPException(status_code=500, detail="Error loading tasks page") from exc


@app.get("/accounts", response_model=list[Account])
def list_accounts() -> list[Account]:
    """Return all accounts in the system."""
    with get_session() as session:
        try:
            accounts = session.exec(select(Account)).all()
            # Return plain dicts to avoid serialization issues with SQLModel under Pydantic v2.
            return [acc.model_dump() for acc in accounts]
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
            return account.model_dump()
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
            return existing_account.model_dump()
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


@app.get("/tasks", response_model=list[Task])
def list_tasks() -> list[Task]:
    """Return all tasks in the system."""
    with get_session() as session:
        try:
            tasks = session.exec(select(Task)).all()
            return [tsk.model_dump() for tsk in tasks]
        except SQLAlchemyError as exc:
            session.rollback()
            logger.exception("Database error while listing tasks")
            raise HTTPException(
                status_code=500,
                detail="Database error while listing tasks",
            ) from exc


@app.post("/tasks", response_model=Task)
def create_task(task: Task) -> Task:
    """Create a new task with database error handling."""
    with get_session() as session:
        try:
            session.add(task)
            session.commit()
            session.refresh(task)
            return task.model_dump()
        except SQLAlchemyError as exc:
            session.rollback()
            logger.exception("Database error while creating a task")
            raise HTTPException(
                status_code=500,
                detail="Database error while creating task",
            ) from exc


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: Task) -> Task:
    """Update an existing task."""
    with get_session() as session:
        try:
            existing_task = session.get(Task, task_id)
            if existing_task is None:
                raise HTTPException(status_code=404, detail="Task not found")

            existing_task.title = task.title
            existing_task.status = task.status
            # Accept either a datetime object or ISO string for due_date
            if isinstance(task.due_date, str):
                existing_task.due_date = datetime.fromisoformat(task.due_date)
            else:
                existing_task.due_date = task.due_date
            existing_task.account_id = task.account_id

            session.add(existing_task)
            session.commit()
            session.refresh(existing_task)
            return existing_task.model_dump()
        except SQLAlchemyError as exc:
            session.rollback()
            logger.exception("Database error while updating a task")
            raise HTTPException(
                status_code=500,
                detail="Database error while updating task",
            ) from exc


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int) -> dict[str, bool]:
    """Remove a task from the system."""
    with get_session() as session:
        try:
            task = session.get(Task, task_id)
            if task is None:
                raise HTTPException(status_code=404, detail="Task not found")
            session.delete(task)
            session.commit()
            return {"ok": True}
        except SQLAlchemyError as exc:
            session.rollback()
            logger.exception("Database error while deleting a task")
            raise HTTPException(
                status_code=500,
                detail="Database error while deleting task",
            ) from exc
