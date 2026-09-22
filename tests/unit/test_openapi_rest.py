"""Unit tests for OpenAPI schema generation and REST API gateway."""

from __future__ import annotations

import pytest
from starlette.testclient import TestClient

from godot_ai.remote import RemoteGodotClient, RemoteGodotError
from godot_ai.transport.openapi import generate_openapi_spec
from tests.conftest import create_test_server


@pytest.fixture(scope="module")
def server_instance():
    return create_test_server(ws_port=0)


@pytest.mark.asyncio
async def test_generate_openapi_spec(server_instance):
    spec = await generate_openapi_spec(server_instance, server_url="https://api.example.com")
    assert spec["openapi"] == "3.1.0"
    assert "paths" in spec
    assert "/api/v1/call" in spec["paths"]
    assert "/api/v1/tools/body_manage" in spec["paths"]
    assert "/api/v1/tools/world_manage" in spec["paths"]
    assert "/api/v1/tools/cloud_manage" in spec["paths"]
    assert spec["servers"][0]["url"] == "https://api.example.com"


def test_rest_gateway_endpoints(server_instance):
    app = server_instance.http_app()
    client = TestClient(app, base_url="http://127.0.0.1:8000")

    # OpenAPI endpoint
    res = client.get("/openapi.json")
    assert res.status_code == 200
    schema = res.json()
    assert schema["openapi"] == "3.1.0"
    assert schema["info"]["version"] == "5.0.25"

    # Status endpoint
    res = client.get("/api/v1/status")
    assert res.status_code == 200
    status_data = res.json()
    assert status_data["status"] == "online"
    assert status_data["version"] == "5.0.25"

    # List tools endpoint
    res = client.get("/api/v1/tools")
    assert res.status_code == 200
    tools_data = res.json()
    assert "tools" in tools_data
    assert tools_data["count"] >= 96


def test_remote_godot_client_headers():
    client = RemoteGodotClient("http://localhost:8000", auth_token="secret-123")
    headers = client._make_headers()
    assert headers["Authorization"] == "Bearer secret-123"
    assert headers["X-Godot-AI-Key"] == "secret-123"
    assert headers["Content-Type"] == "application/json"


def test_remote_godot_error():
    err = RemoteGodotError("test message", status_code=404, data={"detail": "not found"})
    assert str(err) == "test message"
    assert err.status_code == 404
    assert err.data == {"detail": "not found"}
