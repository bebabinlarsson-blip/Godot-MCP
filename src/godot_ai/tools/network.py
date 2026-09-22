"""MCP tool for Godot networking and socket scaffolding."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import network as network_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Networking and Socket Scaffolding.

Ops:
  * scaffold_tcp_server(parent_path="", port=8080, bind_address="*", node_name="TcpServer")
        Scaffold a TCP server node in the current scene.

  * scaffold_websocket_peer(parent_path="", url="", node_name="WebSocketClient")
        Scaffold a WebSocket peer node in the current scene.

  * scaffold_udp_peer(parent_path="", port=9000, node_name="UdpPeer")
        Scaffold a UDP packet peer node in the current scene.

  * get_network_interfaces()
        List local network IP addresses and adapter interfaces.
"""


def register_network_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="network_manage",
        description=_DESCRIPTION,
        ops={
            "scaffold_tcp_server": network_handlers.network_scaffold_tcp_server,
            "scaffold_websocket_peer": network_handlers.network_scaffold_websocket_peer,
            "scaffold_udp_peer": network_handlers.network_scaffold_udp_peer,
            "get_network_interfaces": network_handlers.network_get_network_interfaces,
        },
        read_resource_forms={
            "get_network_interfaces": None,
        },
    )
