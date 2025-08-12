import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

# Use an in-memory SQLite database for isolated tests
os.environ["DATABASE_URL"] = "sqlite://"

from app.main import app  # noqa: E402  # Import after setting DATABASE_URL
from app.database import engine


@pytest.fixture(name="client")
def client_fixture():
    """Provide a TestClient for UI routes with a fresh database."""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with TestClient(app) as client:
        yield client


def test_dashboard_route(client):
    """Dashboard page should render successfully."""
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "Dashboard" in response.text
