"""Handler functions routing cloud bridge and tunnel status commands to Godot."""

from __future__ import annotations

from typing import Any

from godot_ai.runtime.direct import DirectRuntime


async def cloud_get_tunnel_status(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """Check cloud tunnel and REST gateway operational status."""
    return await runtime.send_command("cloud_get_tunnel_status", {}, timeout=10.0)


async def cloud_get_action_schema_url(
    runtime: DirectRuntime,
    host: str = "http://127.0.0.1:8000",
) -> dict[str, Any]:
    """Get OpenAPI schema URL and setup instructions for ChatGPT Custom GPT."""
    params: dict[str, Any] = {"host": host}
    return await runtime.send_command("cloud_get_action_schema_url", params, timeout=10.0)


async def cloud_test_cloud_connection(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """Test round-trip responsiveness between Godot editor and gateway."""
    return await runtime.send_command("cloud_test_cloud_connection", {}, timeout=10.0)
