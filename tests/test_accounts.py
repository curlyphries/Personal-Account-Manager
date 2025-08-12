import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session
from sqlalchemy.exc import SQLAlchemyError

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


def test_create_account(client):
    response = client.post("/accounts", json={"name": "Test"})
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Test"
    assert "id" in body


def test_list_accounts(client):
    client.post("/accounts", json={"name": "A"})
    client.post("/accounts", json={"name": "B"})
    response = client.get("/accounts")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_account(client):
    created = client.post("/accounts", json={"name": "Old"}).json()
    acc_id = created["id"]
    response = client.put(f"/accounts/{acc_id}", json={"name": "New"})
    assert response.status_code == 200
    assert response.json()["name"] == "New"


def test_delete_account(client):
    created = client.post("/accounts", json={"name": "Delete"}).json()
    acc_id = created["id"]
    response = client.delete(f"/accounts/{acc_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert client.get("/accounts").json() == []


def test_create_account_db_error(client, monkeypatch):
    def fail_add(self, obj):  # pragma: no cover - only used for error path
        raise SQLAlchemyError("failure")

    monkeypatch.setattr(Session, "add", fail_add)
    response = client.post("/accounts", json={"name": "Err"})
    assert response.status_code == 500
    assert response.json()["detail"] == "Database error while creating account"


def test_list_accounts_db_error(client, monkeypatch):
    def fail_exec(self, *args, **kwargs):  # pragma: no cover - only used for error path
        raise SQLAlchemyError("failure")

    monkeypatch.setattr(Session, "exec", fail_exec)
    response = client.get("/accounts")
    assert response.status_code == 500
    assert response.json()["detail"] == "Database error while listing accounts"


def test_update_account_db_error(client, monkeypatch):
    acc_id = client.post("/accounts", json={"name": "Old"}).json()["id"]

    def fail_commit(self):  # pragma: no cover - only used for error path
        raise SQLAlchemyError("failure")

    monkeypatch.setattr(Session, "commit", fail_commit)
    response = client.put(f"/accounts/{acc_id}", json={"name": "New"})
    assert response.status_code == 500
    assert response.json()["detail"] == "Database error while updating account"


def test_delete_account_db_error(client, monkeypatch):
    acc_id = client.post("/accounts", json={"name": "Old"}).json()["id"]

    def fail_commit(self):  # pragma: no cover - only used for error path
        raise SQLAlchemyError("failure")

    monkeypatch.setattr(Session, "commit", fail_commit)
    response = client.delete(f"/accounts/{acc_id}")
    assert response.status_code == 500
    assert response.json()["detail"] == "Database error while deleting account"
