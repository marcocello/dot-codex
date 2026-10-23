"""Fast API checks on SQLite; deployment proof must also use PostgreSQL + migrations."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.db import Base
from app.main import create_app
from app.settings import Settings


@pytest.fixture
def client(tmp_path):
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}")
    with TestClient(create_app(settings)) as test_client:
        Base.metadata.create_all(test_client.app.state.engine)
        yield test_client


def test_notes_are_trimmed_and_persist_across_requests(client):
    assert client.get("/api/notes").json() == []
    response = client.post("/api/notes", json={"text": "  First note  "})
    assert response.status_code == 201
    note = response.json()
    assert isinstance(note["id"], int)
    assert note["text"] == "First note"
    assert client.get("/api/notes").json() == [note]


@pytest.mark.parametrize("text", ["", " \n\t ", "x" * 501, None, 123])
def test_invalid_notes_are_rejected_without_writes(client, text):
    assert client.post("/api/notes", json={"text": text}).status_code == 422
    assert client.get("/api/notes").json() == []


def test_maximum_length_note_is_accepted(client):
    assert client.post("/api/notes", json={"text": "x" * 500}).status_code == 201


def test_readiness_checks_database_while_liveness_does_not(client, monkeypatch):
    assert client.get("/api/ready").status_code == 200

    def unavailable():
        raise OperationalError("SELECT 1", {}, Exception("unavailable"))

    monkeypatch.setattr(client.app.state.engine, "connect", unavailable)
    assert client.get("/api/health").json() == {"status": "ok"}
    response = client.get("/api/ready")
    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}
