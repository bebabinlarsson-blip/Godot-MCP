"""Handler functions routing networking commands to Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def network_scaffold_tcp_server(
    runtime: DirectRuntime,
    parent_path: str = "",
    port: int = 8080,
    bind_address: str = "*",
    node_name: str = "TcpServer",
) -> dict[str, Any]:
    """Scaffold a TCP server node in the current scene."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "port": port,
        "bind_address": bind_address,
        "node_name": node_name,
    }
    return await runtime.send_command("network_scaffold_tcp_server", params, timeout=10.0)


async def network_scaffold_websocket_peer(
    runtime: DirectRuntime,
    parent_path: str = "",
    url: str = "",
    node_name: str = "WebSocketClient",
) -> dict[str, Any]:
    """Scaffold a WebSocket peer node in the current scene."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "url": url,
        "node_name": node_name,
    }
    return await runtime.send_command("network_scaffold_websocket_peer", params, timeout=10.0)


async def network_scaffold_udp_peer(
    runtime: DirectRuntime,
    parent_path: str = "",
    port: int = 9000,
    node_name: str = "UdpPeer",
) -> dict[str, Any]:
    """Scaffold a UDP packet peer node in the current scene."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "parent_path": parent_path,
        "port": port,
        "node_name": node_name,
    }
    return await runtime.send_command("network_scaffold_udp_peer", params, timeout=10.0)


async def network_get_network_interfaces(
    runtime: DirectRuntime,
) -> dict[str, Any]:
    """List local network IP addresses and adapter interfaces."""
    return await runtime.send_command("network_get_network_interfaces", {}, timeout=10.0)
