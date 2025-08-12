import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# Use an in-memory SQLite database for isolated tests
os.environ["DATABASE_URL"] = "sqlite://"

from app.main import app  # noqa: E402  # Import after setting DATABASE_URL
from app.database import engine


@pytest.fixture(name="client")
def client_fixture():
    """Provide a TestClient with a fresh database for each test."""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with TestClient(app) as client:
        yield client


def create_account(client):
    """Helper to create a sample account and return its ID."""
    return client.post("/accounts", json={"name": "Owner"}).json()["id"]


def test_create_task(client):
    acc_id = create_account(client)
    payload = {"title": "Call client", "account_id": acc_id}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Call client"
    assert body["account_id"] == acc_id


def test_list_tasks(client):
    acc_id = create_account(client)
    client.post("/tasks", json={"title": "A", "account_id": acc_id})
    client.post("/tasks", json={"title": "B", "account_id": acc_id})
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_task(client):
    acc_id = create_account(client)
    created = client.post("/tasks", json={"title": "Old", "account_id": acc_id}).json()
    task_id = created["id"]
    new_due = datetime.utcnow().isoformat()
    response = client.put(
        f"/tasks/{task_id}",
        json={"title": "New", "status": "done", "due_date": new_due, "account_id": acc_id},
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == "New"
    assert updated["status"] == "done"
    assert updated["due_date"] == new_due


def test_delete_task(client):
    acc_id = create_account(client)
    task_id = client.post("/tasks", json={"title": "Cleanup", "account_id": acc_id}).json()["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert client.get("/tasks").json() == []


def test_create_task_db_error(client, monkeypatch):
    acc_id = create_account(client)

    def fail_add(self, obj):  # pragma: no cover - only used for error path
        raise SQLAlchemyError("failure")

    monkeypatch.setattr(Session, "add", fail_add)
    response = client.post("/tasks", json={"title": "Err", "account_id": acc_id})
    assert response.status_code == 500
    assert response.json()["detail"] == "Database error while creating task"


def test_list_tasks_db_error(client, monkeypatch):
    def fail_exec(self, *args, **kwargs):  # pragma: no cover - only used for error path
        raise SQLAlchemyError("failure")

    monkeypatch.setattr(Session, "exec", fail_exec)
    response = client.get("/tasks")
    assert response.status_code == 500
    assert response.json()["detail"] == "Database error while listing tasks"


def test_update_task_db_error(client, monkeypatch):
    acc_id = create_account(client)
    task_id = client.post("/tasks", json={"title": "Old", "account_id": acc_id}).json()["id"]

    def fail_commit(self):  # pragma: no cover - only used for error path
        raise SQLAlchemyError("failure")

    monkeypatch.setattr(Session, "commit", fail_commit)
    response = client.put(f"/tasks/{task_id}", json={"title": "New", "account_id": acc_id})
    assert response.status_code == 500
    assert response.json()["detail"] == "Database error while updating task"


def test_delete_task_db_error(client, monkeypatch):
    acc_id = create_account(client)
    task_id = client.post("/tasks", json={"title": "Old", "account_id": acc_id}).json()["id"]

    def fail_commit(self):  # pragma: no cover - only used for error path
        raise SQLAlchemyError("failure")

    monkeypatch.setattr(Session, "commit", fail_commit)
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 500
    assert response.json()["detail"] == "Database error while deleting task"

