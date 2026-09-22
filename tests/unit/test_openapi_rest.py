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
    # Compact mode for ChatGPT Custom GPT Actions (strictly <= 25 ops, under OpenAI 30-op cap)
    spec_compact = await generate_openapi_spec(
        server_instance, server_url="https://api.example.com", mode="compact"
    )
    assert spec_compact["openapi"] == "3.1.0"
    assert "paths" in spec_compact
    assert "/api/v1/call" in spec_compact["paths"]
    assert len(spec_compact["paths"]) <= 25
    assert spec_compact["servers"][0]["url"] == "https://api.example.com"

    # Full mode for unrestricted REST clients (all 100 tools)
    spec_full = await generate_openapi_spec(
        server_instance, server_url="https://api.example.com", mode="full"
    )
    assert len(spec_full["paths"]) >= 100


def test_rest_gateway_endpoints(server_instance):
    app = server_instance.http_app()
    client = TestClient(app, base_url="http://127.0.0.1:8000")

    # Landing page HTML endpoint (for web browsing AI / humans)
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "Godot AI Remote Engine Bridge" in res_root.text
    assert "Instructions for ChatGPT" in res_root.text

    # Landing page JSON format
    res_json = client.get("/?format=json")
    assert res_json.status_code == 200
    assert res_json.json()["status"] == "online"
    assert res_json.json()["version"] == "5.0.27"

    # OpenAPI compact endpoint (default)
    res = client.get("/openapi.json")
    assert res.status_code == 200
    schema = res.json()
    assert schema["openapi"] == "3.1.0"
    assert schema["info"]["version"] == "5.0.27"
    assert len(schema["paths"]) <= 25

    # OpenAPI full endpoint
    res = client.get("/openapi-full.json")
    assert res.status_code == 200
    schema_full = res.json()
    assert len(schema_full["paths"]) >= 100

    # Status endpoint
    res = client.get("/api/v1/status")
    assert res.status_code == 200
    status_data = res.json()
    assert status_data["status"] == "online"
    assert status_data["version"] == "5.0.27"

    # List tools endpoint
    res = client.get("/api/v1/tools")
    assert res.status_code == 200
    tools_data = res.json()
    assert "tools" in tools_data
    assert tools_data["count"] == 100

    # Universal call endpoint routing
    res_call_missing = client.get("/api/v1/call")
    assert res_call_missing.status_code == 400
    assert "Missing 'tool' parameter" in res_call_missing.json()["error"]

    res_call_get = client.get("/api/v1/call?tool=editor_state")
    assert res_call_get.json()["tool"] == "editor_state"

    # Tree endpoint routing
    res_tree = client.get("/api/v1/tree")
    assert res_tree.status_code in (200, 400)


def test_remote_godot_client_headers():
    client = RemoteGodotClient("http://localhost:8000", auth_token="secret-123")
    headers = client._make_headers()
    assert headers["Authorization"] == "Bearer secret-123"
    assert headers["X-Godot-AI-Key"] == "secret-123"
    assert client._make_headers()["User-Agent"] == "GodotAI-RemoteClient/5.0.27"
    assert headers["Content-Type"] == "application/json"


def test_remote_godot_error():
    err = RemoteGodotError("test message", status_code=404, data={"detail": "not found"})
    assert str(err) == "test message"
    assert err.status_code == 404
    assert err.data == {"detail": "not found"}
