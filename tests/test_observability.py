"""Offline authentication checks: no tracing services or model calls."""

import importlib

import pytest
from fastapi.testclient import TestClient

server = importlib.import_module("server.app")


@pytest.fixture
def client(world, tmp_path, monkeypatch):
    monkeypatch.setattr(server, "SESSIONS_DB", tmp_path / "sessions.db")
    monkeypatch.setattr(server, "_SESSIONS", {})
    monkeypatch.setenv("CARTWHEEL_DEV_SECRET", "offline-auth-test-secret")

    def unexpected_agent_call(*args, **kwargs):
        pytest.fail("Unauthorized requests must not reach the agent")

    monkeypatch.setattr(server, "build_agent", unexpected_agent_call)
    # No context manager: skip service startup and Langfuse initialization.
    return TestClient(server.app)


def test_session_rejects_claimed_role_mismatch(client):
    response = client.post("/sessions", json={"user_id": 1, "role": "support"})
    assert response.status_code == 403
    assert response.json()["detail"] == "role does not match stored user"
    assert server._SESSIONS == {}


def test_token_cannot_authorize_another_session(client):
    first = client.post("/sessions", json={"user_id": 1, "role": "shopper"})
    second = client.post("/sessions", json={"user_id": 1, "role": "shopper"})
    assert first.status_code == second.status_code == 200
    first, second = first.json(), second.json()
    assert first["session_id"] != second["session_id"]
    response = client.post(
        f"/sessions/{second['session_id']}/messages",
        headers={"Authorization": f"Bearer {first['token']}"},
        json={"message": "Show me order 4127."},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "token is for another session"
