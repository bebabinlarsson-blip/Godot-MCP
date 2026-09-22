"""Handler functions routing HTTP and networking commands
to the connected Godot runtime.
"""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def http_scaffold_http_request(
    runtime: DirectRuntime,
    parent_path: str = "",
    name: str = "HTTPRequest",
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Scaffold an HTTPRequest node into the scene tree."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "name": name,
        "timeout": timeout,
    }
    return await runtime.send_command("http_scaffold_http_request", params, timeout=10.0)


async def http_send_request(
    runtime: DirectRuntime,
    url: str,
    method: str = "GET",
    headers: list[str] | None = None,
    body: str = "",
    timeout: float = 10.0,
) -> dict[str, Any]:
    """Execute an in-engine HTTP request via Godot's HTTPRequest node."""
    params: dict[str, Any] = {
        "url": url,
        "method": method,
        "headers": headers or [],
        "body": body,
        "timeout": timeout,
    }
    return await runtime.send_command("http_send_request", params, timeout=timeout + 5.0)


async def http_download_file(
    runtime: DirectRuntime,
    url: str,
    target_path: str,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Download a remote file into the project virtual filesystem."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "url": url,
        "target_path": target_path,
        "timeout": timeout,
    }
    return await runtime.send_command("http_download_file", params, timeout=timeout + 5.0)
